import math, re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from app.config import EMBEDDING_MODEL, RERANKER_MODEL, TOP_K_DENSE, TOP_K_SPARSE, TOP_K_FINAL
from app.retrieval.chunker import extract_policy

class BM25:
    def __init__(self, docs,k1=1.5,b=.75):
        self.docs=[re.findall(r"\b\w+\b",d.lower()) for d in docs]; self.k1=k1; self.b=b
        self.avgdl=sum(map(len,self.docs))/max(1,len(self.docs)); self.df={}
        for d in self.docs:
            for t in set(d): self.df[t]=self.df.get(t,0)+1
        self.N=len(self.docs)
    def scores(self,q):
        terms=re.findall(r"\b\w+\b",q.lower()); out=np.zeros(self.N)
        for i,d in enumerate(self.docs):
            counts={}
            for t in d: counts[t]=counts.get(t,0)+1
            for t in terms:
                if t not in counts: continue
                df=self.df.get(t,0); idf=math.log(1+(self.N-df+0.5)/(df+0.5))
                out[i]+=idf*counts[t]*(self.k1+1)/(counts[t]+self.k1*(1-self.b+self.b*len(d)/max(self.avgdl,1)))
        return out

class HybridRetriever:
    """Hybrid RAG: lexical BM25 + dense latent-semantic vectors + RRF + cross-encoder reranking."""
    def __init__(self, policy_path):
        self.chunks=extract_policy(policy_path); self.texts=[c["text"] for c in self.chunks]
        self.bm25=BM25(self.texts)
        self.vectorizer=TfidfVectorizer(stop_words="english",ngram_range=(1,2),min_df=1)
        X=self.vectorizer.fit_transform(self.texts)
        # Dense semantic representation without requiring a hosted model.
        n_comp=max(2,min(128,X.shape[1]-1,X.shape[0]-1)) if min(X.shape)<3 else min(128,X.shape[1]-1,X.shape[0]-1)
        self.svd=TruncatedSVD(n_components=max(2,n_comp),random_state=42)
        self.embeddings=self.svd.fit_transform(X); self.embeddings/=np.linalg.norm(self.embeddings,axis=1,keepdims=True)+1e-12
        try:
            from sentence_transformers import SentenceTransformer, CrossEncoder
            self.semantic_model=SentenceTransformer(EMBEDDING_MODEL)
            self.embeddings=self.semantic_model.encode(self.texts,normalize_embeddings=True,show_progress_bar=False)
            self.reranker=CrossEncoder(RERANKER_MODEL)
        except Exception:
            self.semantic_model=None; self.reranker=None

    def search(self,query,top_k=TOP_K_FINAL):
        if self.semantic_model:
            qv=self.semantic_model.encode([query],normalize_embeddings=True)[0]
        else:
            qv=self.svd.transform(self.vectorizer.transform([query]))[0]
            qv/=np.linalg.norm(qv)+1e-12
        dense_scores=np.dot(self.embeddings,qv)
        sparse_scores=self.bm25.scores(query)
        dense_idx=np.argsort(-dense_scores)[:TOP_K_DENSE]; sparse_idx=np.argsort(-sparse_scores)[:TOP_K_SPARSE]
        ranks={}
        for rank,i in enumerate(dense_idx,1): ranks[i]=ranks.get(i,0)+1/(60+rank)
        for rank,i in enumerate(sparse_idx,1): ranks[i]=ranks.get(i,0)+1/(60+rank)
        candidates=sorted(ranks,key=ranks.get,reverse=True)[:max(top_k*2,top_k)]
        if self.reranker:
            rr=self.reranker.predict([(query,self.texts[i]) for i in candidates])
            candidates=[i for _,i in sorted(zip(rr,candidates),reverse=True)]
        else:
            # Transparent local reranking: lexical overlap + dense similarity.
            qterms=set(re.findall(r"\b\w+\b",query.lower()))
            def score(i):
                terms=set(re.findall(r"\b\w+\b",self.texts[i].lower()))
                overlap=len(qterms & terms)/max(1,len(qterms))
                return .55*overlap+.45*float(dense_scores[i])
            candidates=sorted(candidates,key=score,reverse=True)
        out=[]
        for i in candidates[:top_k]:
            c=dict(self.chunks[i]); c.update(dense_score=float(dense_scores[i]),
                sparse_score=float(sparse_scores[i]),fusion_score=float(ranks[i]),retrieval_rank=len(out)+1)
            out.append(c)
        return out
