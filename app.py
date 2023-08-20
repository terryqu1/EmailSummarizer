from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from flask import Flask, render_template
import os
import openai
from langchain.document_loaders import UnstructuredEmailLoader
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
 
app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set!")

     # Set API key for OPENAI library
openai.api_key = openai_api_key

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# List to keep track of file destinations
file_destinations = []
summary_list = []

@app.route('/')
def index():
    return render_template('upload.html', files=file_destinations, summaries=summary_list)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Save the file destination
        file_destinations.append(filename)
        path = "C:\\Users\\terry\\Documents\\todo-app\\" + filename

        # Define prompt
        prompt_template = """Write a concise summary of the following: "{text}"
        CONCISE SUMMARY:"""

        prompt = PromptTemplate.from_template(prompt_template)

        loader = UnstructuredEmailLoader(path, mode = "elements")
        docs = loader.load()

        # Define LLM
        llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.5)
        llm_chain = LLMChain(llm=llm, prompt = prompt)

        # Set up stuff chain
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name="text"
        )

        summary_list.append(stuff_chain.run(docs))
        return render_template('upload.html', files=file_destinations, summaries=summary_list)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
