import json
import os

from flask import Flask, request
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus

model_name = r'D:\m3e-base'
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
index_params = {"metric_type": "IP"}
search_params = {"metric_type": "IP"}
connection_args = {"host": "192.168.11.78", "port": "19530"}
vdb = Milvus(
    embedding_function=hf,
    connection_args=connection_args,
    index_params=index_params,
    search_params=search_params,
    drop_old=True,
)


def scan_dir_to_vdb(uploads_dir='uploads'):
    for filename in os.listdir(uploads_dir):
        filepath = os.path.join(uploads_dir, filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.split_documents(pages)
            vdb.add_documents(docs)


class Response:
    @staticmethod
    def success(code: int = 0, desc: str = "操作成功", data: any = None) -> str:
        return json.dumps({
            "code": code,
            "desc": desc,
            "data": data
        })

    @staticmethod
    def failure(code: int = -1, desc: str = "操作失败", data: any = None) -> str:
        return json.dumps({
            "code": code,
            "desc": desc,
            "data": data
        })


app = Flask(__name__)


@app.route('/add_doc', methods=['POST'])
def add_doc():
    req = request.json
    if 'filepath' not in req or not req['filepath']:
        return Response.failure(
            desc='参数不符合要求, 未找到filepath字段或字段为空',
        )
    try:
        loader = PyPDFLoader(req['filepath'])
        pages = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(pages)
        vdb.add_documents(docs)
        return Response.success(
            desc='文档向量化成功',
        )
    except Exception as e:
        print(e)
        return Response.failure(
            desc='文档向量化异常',
        )


@app.route('/query', methods=['POST'])
def query():
    req = request.json
    if 'prompt' not in req or not req['prompt']:
        return Response.failure(
            desc='参数不符合要求, 未找到prompt字段或字段为空',
        )
    results = vdb.similarity_search_with_score(req['prompt'])
    filtered_results = [item for item in results if item[1] >= 0.8]
    if len(filtered_results) == 0:
        return Response.failure(
            desc='未找到符合要求的内容',
        )

    data = []
    for doc in filtered_results:
        data.append({
            'content': doc[0].page_content,
            'source': doc[0].metadata['source'],
            'page_num': doc[0].metadata['page'],
            'score': doc[1]
        })

    return Response.success(
        data=data,
        desc=f'成功查找到{len(data)}个符合要求的数据',
    )


if __name__ == "__main__":
    scan_dir_to_vdb()
    app.run(host="0.0.0.0", port=5000)
