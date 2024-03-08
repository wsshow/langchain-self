import json
import os

from flask import Flask, request
from langchain.document_loaders import UnstructuredFileLoader, UnstructuredMarkdownLoader, \
    UnstructuredPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import MarkdownTextSplitter, CharacterTextSplitter
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


def load_txt_file(filepath):
    loader = UnstructuredFileLoader(filepath)
    docs = loader.load()
    return docs


def load_md_file(filepath):
    loader = UnstructuredMarkdownLoader(filepath)
    docs = loader.load()
    return docs


def load_pdf_file(filepath):
    loader = UnstructuredPDFLoader(filepath)
    docs = loader.load()
    return docs


def load_txt_splitter(txt_file, chunk_size=200, chunk_overlap=20):
    docs = load_txt_file(txt_file)
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_splitter.split_documents(docs)
    return split_docs


def load_md_splitter(md_file, chunk_size=200, chunk_overlap=20):
    docs = load_md_file(md_file)
    text_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_splitter.split_documents(docs)
    return split_docs


def load_pdf_splitter(pdf_file, chunk_size=200, chunk_overlap=20):
    docs = load_pdf_file(pdf_file)
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_splitter.split_documents(docs)
    return split_docs


def file_to_vdb(filepath):
    split_docs: list[Document] = []
    if filepath.endswith('.pdf'):
        split_docs = load_pdf_splitter(filepath)
    elif filepath.endswith('.md'):
        split_docs = load_md_splitter(filepath)
    elif filepath.endswith('.txt'):
        split_docs = load_txt_splitter(filepath)
    vdb.add_documents(split_docs)


def scan_dir_to_vdb(uploads_dir='uploads'):
    for filename in os.listdir(uploads_dir):
        filepath = os.path.join(uploads_dir, filename)
        file_to_vdb(filepath)


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
        file_to_vdb(req['filepath'])
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
