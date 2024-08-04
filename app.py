from flask import Flask, render_template, request, jsonify, redirect, session
import uuid
import os
from dotenv import load_dotenv
import pandas as pd
from langchain.chains import LLMChain
from langchain.chains.constitutional_ai.models import ConstitutionalPrinciple
from langchain.chains.constitutional_ai.base import ConstitutionalChain
from langchain_core.prompts import PromptTemplate
import pyrebase
from datetime import datetime
import hashlib
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
import pickle
from subprocess import Popen
from langchain_community.document_loaders import PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

config = {
    "apiKey": "YOUR API KEY",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": ""
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


#Gemini model
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "YOUR API KEY"

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-001")

#OpenAI Embeddings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'na')

#Mongo DB Connection
ATLAS_CONNECTION_STRING = os.getenv('mongo_connection_string', 'na')

# Connect to your Atlas cluster
client = MongoClient(ATLAS_CONNECTION_STRING)

# Define collection and index name
db_name = "Career-Coaching"
collection_name = "data"
atlas_collection = client[db_name][collection_name]
vector_search_index = "vector_search"


vectorStore = MongoDBAtlasVectorSearch(
    atlas_collection, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY), index_name=vector_search_index
)

retriever = vectorStore.as_retriever(
   search_type = "similarity",
   search_kwargs = {"k": 5, "score_threshold": 0.75}
)


def format_docs(docs):
   return "\n\n".join(doc.page_content for doc in docs)

app = Flask(__name__)

app.secret_key = os.getenv("secret_key", "")

 # Secret salt (you should generate and keep this secret)
salt = os.getenv("salt_secret")

# Function to generate a consistent integer hash for an email
def generate_email_integer_hash(email):
    salted_email = salt + email
    sha256 = hashlib.sha256(salted_email.encode()).digest()
    # Take the lower 8 bits of the hash as an integer
    email_hash_8bit = int.from_bytes(sha256[-1:], byteorder='big')
    return email_hash_8bit


# Configure the upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

LIBRE_OFFICE = r"lowriter"

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def convert_to_pdf(input_docx, out_folder):
        p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir',
                out_folder, input_docx])
        print([LIBRE_OFFICE, '--convert-to', 'pdf', input_docx])
        p.communicate() 


questions = {}
c = 0
f_c = 0
education_status = [[]]


@app.get('/')
def resume_upload():
    if "user" in session:

        try:
            session_id = session["user"]
            user_name = session_id.split("@")[0]
            resume_text = pickle.load(open("data_read.pkl", "rb"))[session_id]
            questions[session['user']] = {"education_status":[[]], "cand-details":[], "previous_chat":[]}
            return render_template("home.html", session_id=session_id, user_name=user_name)

        except:
            pass

        questions[session['user']] = {"education_status":[[]], "cand-details":[], "previous_chat":[]}
        c = 0
        print(c, questions, education_status)
        return render_template("index.html")
 
    else:
        return render_template("login.html")



@app.get('/resume_upload2')
def resume_upload2():
    if "user" in session:
        session_id = session["user"]
        user_name = session_id.split("@")[0]
        questions[session['user']] = {"education_status":[[]], "cand-details":[], "previous_chat":[]}
        c = 0
        print(c, questions, education_status)
        return render_template("index.html", user_name=user_name)
 
    else:
        return render_template("login.html")


@app.get("/users_list")
def users_list():
    if "user" in session:

        session_id = session["user"]
        user_name = session_id.split("@")[0]

        def feedback_extract(user_id):

            try:
                #Extracting Feedback
                val = dict(db.child("users").child(user_id).child("feedback").get().val())
                feedback = val["feedback"]
                email = val["user_email"]


                #Extracting Dates
                dates_used = dict(db.child("users").child(user_id).child("dates_used").get().val())
                dates_list = list(dates_used.keys())

            
                if len(dates_list) > 1:
                    # Convert the list to a DataFrame
                    df = pd.DataFrame(dates_list, columns=['dates'])

                    # Convert the 'dates' column to datetime format
                    df['dates'] = pd.to_datetime(df['dates'], format='%m-%d-%y')

                    # Sort the DataFrame by the 'dates' column in descending order
                    df_sorted = df.sort_values(by='dates', ascending=False)

                    # Convert the sorted DataFrame back to a list
                    sorted_dates = df_sorted['dates'].dt.strftime('%m-%d-%y').tolist()

                    final_date = sorted_dates[0]

                else:
                    final_date = dates_list[0]

                return [email, feedback, final_date]
            
            except:
                pass


        users_id_list = dict(db.child("users").get().val())

        user_id = list(users_id_list.keys())

        lx = []

        for i in user_id:
            val = feedback_extract(i)
            lx.append(val)

        return render_template("table.html", lx = lx, user_name=user_name)

    else:
        return render_template("login.html")

@app.get("/training_page")
def training_page():

    session_id = session["user"]
    user_name = session_id.split("@")[0]
    
    if "admin" in session:
        return render_template("tr2.html", data=False, user_name=user_name)
    
    else:
        return render_template("tr.html", user_name=user_name)


@app.post('/upload_tr')
def upload_tr():
    if 'training_data' not in request.files:
        return 'No file part'
    
    file = request.files['training_data']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        file_path = f"{app.config['UPLOAD_FOLDER']}/" + file.filename
        file.save(file_path)
        
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            pass


        elif file_extension == '.docx':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-5]+".pdf"
            

        elif file_extension == '.doc':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-4]+".pdf"


        elif file_extension == '.txt':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-4]+".pdf"

        elif file_extension == '.rtf':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-4]+".pdf"

        else:
            return "Unsupported file type."
    

        loader = PDFMinerLoader(file_path)
        data = loader.load()


        # Split PDF into documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n\n", "\n", "(?<=\. )", " "], length_function=len)
        docs = text_splitter.split_documents(data)

        vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents = docs,
        embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
        collection = atlas_collection,
        index_name = vector_search_index
        )

        return render_template("tr2.html", data=True)

    else:
        return "Upload supported file types only (DOC, DOCX, RTF, TXT)"
    



@app.post('/upload')
def upload():
    if 'files' not in request.files:
        return 'No file part'
    
    file = request.files['files']

    if file.filename == '':
        return 'No selected file'
    

    if file:
        file_path = f"{app.config['UPLOAD_FOLDER']}/" + file.filename
        file.save(file_path)
        
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            pass


        elif file_extension == '.docx':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-5]+".pdf"
            

        elif file_extension == '.doc':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-4]+".pdf"


        elif file_extension == '.txt':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-4]+".pdf"

        elif file_extension == '.rtf':
            convert_resume =  convert_to_pdf(file_path, app.config['UPLOAD_FOLDER'])
            file_path = file_path[:-4]+".pdf"

        else:
            return "Unsupported file type."
    

        loader = PDFMinerLoader(file_path)
        data = loader.load()

        # Iterate through each Document object in the list and concatenate the text with newline separator
        pdf_text = '\n'.join([doc.page_content for doc in data])

        session_id = session["user"]

        if os.path.exists("data_read.pkl"):
            val = pickle.load(open("data_read.pkl", "rb"))
            val[session_id] = pdf_text
            pickle.dump(val, open("data_read.pkl", "wb"))

        else:
            val = {session_id: pdf_text}
            pickle.dump(val, open("data_read.pkl", "wb"))

        # Display the initial message from the bot
        initial_message = "Jarvis: H! I'm here to help Career Counsellors, you can ask any questions related to career counselling"
        return render_template('home.html', initial_message=initial_message, session_id=session_id)


    else:
        return "Upload supported file types only (DOC, DOCX, RTF, TXT)"

@app.get("/index")
def index():
    if "user" in session:
        session_id = session["user"]
        user_name = session_id.split("@")[0]
        return render_template("home.html", user_name=user_name)
    
    else:
        return render_template("login.html")


@app.get("/admin_training_page")
def admin_training_page():
    session_id = session["user"]
    user_name = session_id.split("@")[0]
    return render_template("tr.html", user_name=user_name)


@app.post("/admin_training_page_response")
def admin_training_page_response():

    email = request.form["email"]
    password = request.form["pass"]

    sa_list = db.child("super_admin").get().val()

    if email in sa_list:

        auth = firebase.auth()

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["admin"] = email

        except:
            return "Invalid Username or Password"
        
    else:
        return "Sorry, looks like this email address doesn't have super admin access"
        
    return render_template("tr2.html")
         


@app.get('/reload_user')
def reload_user():
    return redirect("/")
    
@app.get("/login")
def login():
    return render_template("login.html")

@app.post("/login_response")
def login_response():

    email = request.form["email"]
    password = request.form["password"]

    # Get a reference to the auth service
    auth = firebase.auth()

    # Log the user in
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        session["user"] = email
    
        return redirect("/")
    
    except:
        return "INVALID_LOGIN_CREDENTIALS"

    

def check_word_in_string(word, string):

            word_processed = word.replace(" ", "").lower()
            string_processed = string.replace(" ", "").lower()

            return word_processed in string_processed


@app.post('/ask')
def ask_question():
    
    session_id = request.form['session_id']

    user_response = request.form['user_response']

    print(session_id, user_response)

    resume_text = pickle.load(open("data_read.pkl", "rb"))[session_id]

    if session_id not in questions:
        questions[session_id] = {"education_status":[[]], "cand-details":[], "previous_chat":[]}

    questions[session_id]["cand-details"].append(user_response)
    
    c = len(questions[session_id]["cand-details"])
    
    c = c-1

    # print(c, questions)
    
    if c == 0:

        if check_word_in_string("student", questions[session_id]["cand-details"][0]):
            bot_response =  "Are you currently studying for a Bachelor's degree or a Master's degree?"
            questions[session_id]['education_status'][0].append('student')

        elif check_word_in_string("passout", questions[session_id]["cand-details"][0]):
            bot_response =  "Are you planning to pursue Master's Degree: Yes or No?"
            questions[session_id]['education_status'][0].append('passout')

        elif check_word_in_string("work", questions[session_id]["cand-details"][0]):
            bot_response =  "How much Years Of Experience you have?"
            questions[session_id]['education_status'][0].append('working_professional')

        else:
            bot_response =  "Please select one option from Student, Passout, Working Professional!"
            questions[session_id]["cand-details"] = []


    elif c == 1:

        if questions[session_id]['education_status'][0][0] == "student":
            if check_word_in_string("master", questions[session_id]["cand-details"][1]):
                questions[session_id]['education_status'][0].append("Master's Degree")
                bot_response =  "Thankyou for Answering My Questions. Now you can ask any question related to Career Counselling"

           
            elif check_word_in_string("bach", questions[session_id]["cand-details"][1]):
                questions[session_id]['education_status'][0].append("Bachelor's Degree")
                bot_response =  "Thankyou for Answering My Questions. Now you can ask any question related to Career Counselling"

            else:
                bot_response =  "Please select one option from Bachelor's degree or Master's degree!"
                questions[session_id]["cand-details"] = questions[session_id]["cand-details"][:-1]

        
        elif questions[session_id]['education_status'][0][0] == "passout":
            if check_word_in_string("yes", questions[session_id]["cand-details"][1]):
                questions[session_id]['education_status'][0].append("yes")
                bot_response =  "Thankyou for Answering My Questions. Now you can ask any question related to Career Counselling"

            elif check_word_in_string("no", questions[session_id]["cand-details"][1]):
                questions[session_id]['education_status'][0].append("no")
                bot_response =  "Thankyou for Answering My Questions. Now you can ask any question related to Career Counselling"

            else:
                bot_response =  "Please select one option from Yes or No!"
                questions[session_id]["cand-details"] = questions[session_id]["cand-details"][:-1]

                 
        elif questions[session_id]['education_status'][0][0] == "working_professional":
                                
                if str(questions[session_id]["cand-details"][1]).isdigit():
                    questions[session_id]['education_status'][0].append(questions[session_id]["cand-details"][1])
                    bot_response =  "Thankyou for Answering My Questions. Now you can ask any question related to Career Counselling"

                else:
                    bot_response =  "Please share Years Of Experience in Number!"
                    questions[session_id]["cand-details"] = questions[session_id]["cand-details"][:-1]

        
        # else:
        #     bot_response =  "Please select one option from Student, Passout,  Working Professional!"
        #     questions[session_id] = questions[session_id][:-1]

    elif c >= 2:

        def date_exist(user_id):

            #Creating date if noy exists
            try:
                val = dict(db.child("users").child(user_id).child("dates_used").get().val())

                #Extract Todays Date
                today_date = datetime.now().strftime("%m-%d-%y")
                val = val[today_date]

            except:
                try:
                    val = dict(db.child("users").child(user_id).child("dates_used").get().val())

                except:
                    val = {}

                #create date for particular user
                today_date = datetime.now().strftime("%m-%d-%y")

                val[today_date] = 10

                db.child("users").child(user_id).child("dates_used").set(val)


        def request_left(user_id):
            val = dict(db.child("users").child(user_id).child("dates_used").get().val())
            today_date = datetime.now().strftime("%m-%d-%y")
            return val[today_date]

        def decrement_request(user_id):
            val = dict(db.child("users").child(user_id).child("dates_used").get().val())
            today_date = datetime.now().strftime("%m-%d-%y")
            balance = val[today_date]-1
            val[today_date] = balance
            db.child("users").child(user_id).child("dates_used").set(val)

        def feedback_check(user_id):
            try:
                val = dict(db.child("users").child(user_id).child("feedback").get().val())

                #Extract feedback status
                val = val["feedback_status"]
                return val

            except:
                #create date for particular user
                val = {"feedback_status": False}
                db.child("users").child(user_id).child("feedback").set(val)
                return False


        username = session["user"]
        hashed_username = generate_email_integer_hash(username)


        date_exist(hashed_username)

        remaining_request = request_left(hashed_username)

        if remaining_request > 0:

            documents = retriever.get_relevant_documents(questions[session_id]["cand-details"][c])

            data = format_docs(documents)

            if questions[session_id]['education_status'][0][0] == "student":

                category = questions[session_id]['education_status'][0][0]
                degree = questions[session_id]['education_status'][0][1]
                pc = questions[session_id]["previous_chat"]


                career_prompt = PromptTemplate(
                    template="""As a Career Counsellor specializing in {degree} degree students, your mission is to provide empathetic counseling and actionable advice. Listen attentively to their needs, offering tailored solutions that foster growth and success. Remember to approach each interaction with empathy and provide high-level counseling for a brighter future and don't answer questions which are out of context.

                                Also use the data from knowledge base and Resume below while answering the query. If data is present in knowldege base then use this data while counselling the candidate. If data is empty or irrelevant then use your own data for career counselling.

                                Resume: {resume}

                                Knowledge Base: {data}

                                Question: {question}

                                Previous Chat: {pc}

                                Previous chat is a list containing the chats of user and bot in dictionary format. If the list is empty then ignore.

                                Answer:""",
                    input_variables=["question", "degree", "data", "resume", "pc"],
                )

                career_chain = LLMChain(llm=llm, prompt=career_prompt)

                # input_variables = {
                #     "degree": "Computer Science",
                #     "resume": "John Doe, CS graduate with experience in software development, seeking opportunities in AI and ML.",
                #     "data": "John has shown exceptional skills in Python and has completed multiple projects in AI.",
                #     "question": "What career paths should I consider with my background?",
                #     "pc": []
                # }

                # Get the output from the chain
                # bot_response = career_chain.run(question=questions[session_id]["cand-details"][c], degree=degree, data=data, resume=resume_text, pc = pc)
                # print("Answer)", bot_response)
                # print("Career Chain..", bot_response)

                ethical_principle = ConstitutionalPrinciple(
                name="Career Counsellor Bot",
                critique_request="The model should behave as an experienced career counsellor and understand questions well and then provide guidance. If required help the candidate to create resume like a professional and also provide resume template. If response is appropriate then return models initial response as output, dont return no changes needed as output. Also model response should not be generic.",
                revision_request="Rewrite the model's response to be thorough and detailed, directly addressing the user’s concerns with specific, actionable advice. Ensure the tone is empathetic and engaging, typical of a career counsellor with extensive experience in career guidance. If required help the candidate to create resume like professional with resume template. Also model response should not be generic.",
                )

                constitutional_chain = ConstitutionalChain.from_llm(
                chain=career_chain,
                constitutional_principles=[ethical_principle],
                llm=llm,
                verbose=True,
                )

                bot_response = constitutional_chain.run(question=questions[session_id]["cand-details"][c], degree=degree, data=data, resume=resume_text, pc = pc)

                print()
                print("Q)", questions[session_id]["cand-details"][c])
                print("Answer)", bot_response)

                prev_chat = questions[session_id]["cand-details"][c]

                questions[session_id]["previous_chat"].append({"user_question": prev_chat, "bot_response": bot_response})


                print()
                # print(questions[session_id]["previous_chat"])
                print()
                


                decrement_request(hashed_username)

            elif questions[session_id]['education_status'][0][0] == "passout":

                category = questions[session_id]['education_status'][0][0]
                degree = questions[session_id]['education_status'][0][1]
                pc = questions[session_id]["previous_chat"]

                if degree.lower() == "yes":
                    template = """As a Career Counsellor specializing in passout students having interest in doing masters, your mission is to provide empathetic counseling and actionable advice. Listen attentively to their needs, offering tailored solutions that foster growth and success. Remember to approach each interaction with empathy and provide high-level counseling for a brighter future and don't answer questions which are out of context

                                Also use the data from knowledge base and Resume below while answering the query. If data is present in knowldege base then use this data while counselling the candidate. If data is empty or irrelevant then use your own data for career counselling.

                                Resume: {resume}

                                Knowledge Base: {data}

                                Question: {question}

                                Previous Chat: {pc}

                                Previous chat is a list containing the chats of user and bot in dictionary format. If the list is empty then ignore.
                                
                                Answer:"""

                else:
                    template = """As a Career Counsellor specializing in passout students having no interest in doing masters, your mission is to provide empathetic counseling and actionable advice. Listen attentively to their needs, offering tailored solutions that foster growth and success. Remember to approach each interaction with empathy and provide high-level counseling for a brighter future and don't answer questions which are out of context

                                Also use the data from knowledge base and Resume below while answering the query. If data is present in knowldege base then use this data while counselling the candidate. If data is empty or irrelevant then use your own data for career counselling.

                                Resume: {resume}

                                Knowledge Base: {data}

                                Question: {question}

                                Previous Chat: {pc}

                                Previous chat is a list containing the chats of user and bot in dictionary format. If the list is empty then ignore.
                                
                                Answer:"""
                    

                career_prompt = PromptTemplate(
                    template=template,
                    input_variables=["question", "data", "resume", "pc"],
                )
                    
                career_chain = LLMChain(llm=llm, prompt=career_prompt)

                ethical_principle = ConstitutionalPrinciple(
                name="Career Counsellor Bot",
                critique_request="The model should behave as an experienced career counsellor and understand questions well and then provide guidance. If required help the candidate to create resume like a professional and also provide resume template. If response is appropriate then return models initial response as output, dont return no changes needed as output. Also model response should not be generic.",
                revision_request="Rewrite the model's response to be thorough and detailed, directly addressing the user’s concerns with specific, actionable advice. Ensure the tone is empathetic and engaging, typical of a career counsellor with extensive experience in career guidance. If required help the candidate to create resume like professional with resume template. Also model response should not be generic.",
                )

                constitutional_chain = ConstitutionalChain.from_llm(
                chain=career_chain,
                constitutional_principles=[ethical_principle],
                llm=llm,
                verbose=True,
                )

                bot_response = constitutional_chain.run(question=questions[session_id]["cand-details"][c], data=data, resume=resume_text, pc = pc) 

                print()
                print("Q)", questions[session_id]["cand-details"][c])
                print("Answer)", bot_response)
            
                decrement_request(hashed_username)


            elif questions[session_id]['education_status'][0][0] == "working_professional":

                category = questions[session_id]['education_status'][0][0]
                yoe = questions[session_id]['education_status'][0][1]
                pc = questions[session_id]["previous_chat"]

                
                career_prompt = PromptTemplate(
                    template="""As a Career Counsellor specializing in professionals with {yoe} years of experience, your mission is to provide empathetic counseling and actionable advice. Listen attentively to their career aspirations and challenges, offering tailored solutions that foster growth and success. Remember to approach each interaction with empathy, understanding the unique needs of experienced professionals. Provide high-level counseling focused on advancing their careers and achieving long-term goals. Additionally, ensure to stay within the context of their professional experience and avoid answering questions that are out of scope.

                                Also use the data from knowledge base and Resume below while answering the query. If data is present in knowldege base then use this data while counselling the candidate. If data is empty or irrelevant then use your own data for career counselling.

                                Resume: {resume}

                                Knowledge Base: {data}

                                Question: {question}

                                Previous Chat: {pc}

                                Previous chat is a list containing the chats of user and bot in dictionary format. If the list is empty then ignore.
                                
                                Answer:""",
                    input_variables=["question", "data", "yoe", "resume", "pc"],
                )

                career_chain = LLMChain(llm=llm, prompt=career_prompt)

                ethical_principle = ConstitutionalPrinciple(
                name="Career Counsellor Bot",
                critique_request="The model should behave as an experienced career counsellor and understand questions well and then provide guidance. If required help the candidate to create resume like a professional and also provide resume template. If response is appropriate then return models initial response as output, dont return no changes needed as output. Also model response should not be generic.",
                revision_request="Rewrite the model's response to be thorough and detailed, directly addressing the user’s concerns with specific, actionable advice. Ensure the tone is empathetic and engaging, typical of a career counsellor with extensive experience in career guidance. If required help the candidate to create resume like professional with resume template. Also model response should not be generic.",
                )

                constitutional_chain = ConstitutionalChain.from_llm(
                chain=career_chain,
                constitutional_principles=[ethical_principle],
                llm=llm,
                verbose=True,
                )

                bot_response = constitutional_chain.run(question=questions[session_id]["cand-details"][c], yoe=yoe, data=data, resume=resume_text, pc=pc)

                print()
                print("Q)", questions[session_id]["cand-details"][c])
                print("Answer)", bot_response)

                decrement_request(hashed_username)


            else:
                bot_response = "I can't help you with this question"


        else:
            bot_response = "You have reached your daily limit of 10 questions. Please try again tomorrow!"
            questions[session_id] = []


    feedback_required = False

    print("Count", c)

    if c == 4:
        if feedback_check(hashed_username):
            print(feedback_check(hashed_username))
            feedback_required = False

        else:
            print(feedback_check(hashed_username))
            feedback_required = True
   
    return jsonify({'bot_response': bot_response, 'feedback_required': feedback_required})

@app.post('/feedback')
def feedback():
    data = request.get_json()
    session_id = data.get('session_id')
    rating = data.get('rating')
    feedback = data.get('feedback')

    user_id = generate_email_integer_hash(session["user"])

    val = dict(db.child("users").child(user_id).child("feedback").get().val())

    #Add Feedback
    val["feedback_status"] = True
    val["rating"] = rating
    val["feedback"] = feedback
    val["user_email"] = session_id

    print(val)

    db.child("users").child(user_id).child("feedback").set(val)

    print(f"Feedback received: Session ID: {session_id}, Rating: {rating}, Feedback: {feedback}")
    return jsonify({'status': 'success'})

@app.get("/sign_up")
def sign_up():
    return render_template("sign_up.html")

@app.post("/sign_up_response")
def sign_up_response():

    user_name = request.form["username"]
    email = request.form["email"]
    password_1 = request.form["password"]

    try:    
        auth.create_user_with_email_and_password(email, password_1)

    except:
        return "Account already exists"
    

    return render_template("login.html")


@app.get("/logout")
def logout():
    session.pop("user", None)
    return render_template("login.html")

@app.get("/forget_pass")
def forget_pass():
    return render_template("forget_pass.html", show_content=False)

@app.post('/forget_pass_response')
def forget_pass_response():
    email = request.form["email"]
    auth.send_password_reset_email(email)
    return render_template("forget_pass.html", show_content=True)

if __name__ == '__main__':
    app.run(debug=True, port=815, host="0.0.0.0")



