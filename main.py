import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
import time


def run():
    st.set_page_config(
        page_title="SURA quiz",
        page_icon="🔔",
        layout="wide",
    )

if __name__ == "__main__":
    run()

show_error = False



if 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""

if 'edit_mode' not in st.session_state:
    st.session_state['edit_mode'] = False

if 'edit_index' not in st.session_state:
    st.session_state['edit_index'] = None

if 'delete_confirmation' not in st.session_state:
    st.session_state.delete_confirmation = False

if 'select_answer' not in st.session_state:
    st.session_state.select_answer = False

#Audio
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

nombre_usuario = st.session_state['usuario']

# Load quiz data
with open('./content/quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)
data = [dict(item) for item in quiz_data]
num_items = len(quiz_data)

def load_valid_emails(csv_file):
    df = pd.read_csv(csv_file)
    return df['email'].apply(str.lower).tolist()

valid_emails = load_valid_emails('./content/correos.csv')


def save_data(file_name, user_email, total_points, date_responded, elapsed_time):
    data = load_data(file_name)
    new_data = pd.DataFrame([{
        "user_email": user_email,
        "total_points": total_points,
        "date_responded": date_responded,
        "elapsed_time": elapsed_time
    }])
    data = pd.concat([data, new_data], ignore_index=True)
    data.to_csv(file_name, index=False, date_format='%Y-%m-%d %H:%M:%S')  # Specify date_format explicitly

# Function to load existing data or create a new DataFrame if the file doesn't exist
def load_data(file_name):
    try:
        data = pd.read_csv(file_name, parse_dates=['date_responded'], date_format='%Y-%m-%d %H:%M:%S')
        # Sort by 'total_points' descending and 'date_responded' ascending
        data = data.sort_values(by=['total_points', 'elapsed_time', 'date_responded'], ascending=[False, True, True]).reset_index(drop=True)
        return data
    except FileNotFoundError:
        return pd.DataFrame(columns=["user_email", "total_points", "date_responded", "elapsed_time"])
    

def display_leaderboard():
    # Leaderboard section
    st.html("<p class='leaderboard'>Tabla de posiciones</p>")

    leaderboard_data = load_data("./content/leaderboard.csv")
    if not leaderboard_data.empty:
        
        #st.dataframe(leaderboard_data)
        
        # Display the leaderboard
        top_n = 20
        leaderboard_data = leaderboard_data.head(top_n)

        # Specify the columns to display
        columns_to_display = ['user_email', 'total_points', 'date_responded', 'elapsed_time']

        # Loop through each row and display the specified columns
        st.html(f"""
                 <table class='tabla tablah'>
                    <tr>
                        <th>#</th>
                        <th>Usuario</th>
                        <th>Puntos</th>
                        <th>Fecha</th>
                        <th>Tiempo</th>
                    </tr>
                 </table>
                 """)
        i = 1
        for index, row in leaderboard_data.iterrows():

            # Original date string
            date_string = str(row['date_responded'])

            # Convert the string to a datetime object
            date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

            # Format the datetime object to the desired format
            formatted_date = date_obj.strftime("%d/%m/%Y @ %H:%M")



            if i%2==0:
                st.html(f"""<table class='tabla'><tr class='par'><td>{i}</td><td>{row['user_email']}</td><td>{round(row['total_points'],2)}</td><td>{formatted_date}</td><td>{round(row['elapsed_time'],2)}</td></tr></table>""")
            else:
                st.html(f"""<table class='tabla'><tr class='non'><td>{i}</td><td>{row['user_email']}</td><td>{round(row['total_points'],2)}</td><td>{formatted_date}</td><td>{round(row['elapsed_time'],2)}</td></tr></table>""")
            i += 1

    else:
        st.write("Esperando el siguiente puntaje")

def restart_quiz():
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.selected_option = None
        st.session_state.answer_submitted = False
        st.session_state['usuario'] = ""
        st.rerun()

def restart_quiz_without_rerun():
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.selected_option = None
        st.session_state.answer_submitted = False
        st.session_state['usuario'] = ""

def submit_answer():

    # Check if an option has been selected
    if st.session_state.selected_option is not None:
        # Mark the answer as submitted
        st.session_state.answer_submitted = True
        # Check if the selected option is correct
        if st.session_state.selected_option == quiz_data[st.session_state.current_index]['answer']:
            st.session_state.score += 10
    else:
        # If no option selected, show a message and do not mark as submitted
        # st.write("")
        # st.error("Por favor seleccione una opción", icon="🚨")
        st.session_state.select_answer = True
        
def next_question():
    st.session_state.current_index += 1
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False

def display_login():
    st.image("./content/sura.jpg")
    st.markdown('<h1 class="main-title">SURA QUIZ</h1>', unsafe_allow_html=True)
    
    with st.form("my_form"):
        correo = st.text_input("Entrar con correo empresarial", key="correo", value="@segurossura.com.mx")
        invitado = st.text_input("Entrar como invitado (ingresa tu nombre completo)", key="invitado", value="")
        
        # Every form must have a submit button.
        submitted = st.form_submit_button("ENTRAR")
        if submitted:
            correo_lower = correo.lower()
            if correo_lower in valid_emails:
                st.session_state["logged_in"] = True
                st.session_state['usuario'] = correo_lower
                ######### LOGGED IN ################
                st.session_state['start_time'] = datetime.now()  # Record the start time
                st.rerun()
            else:
                if len(invitado)>0:
                    st.session_state["logged_in"] = True
                    st.session_state['usuario'] = invitado
                    ######### LOGGED IN ################
                    st.session_state['start_time'] = datetime.now()  # Record the start time
                    st.rerun()
                else:
                    st.error("No pudimos validar tu correo, ingresa como invitado.")


def display_quiz():
    # Initialize session variables if they do not exist
    default_values = {'current_index': 0, 'current_question': 0, 'score': 0, 'selected_option': None, 'answer_submitted': False}
    for key, value in default_values.items():
        st.session_state.setdefault(key, value)

    # Title and description
    st.markdown('<h1 class="main-title">SURA QUIZ</h1>', unsafe_allow_html=True)

    # Display the question and answer options
    if len(quiz_data) > 0:
        question_item = quiz_data[st.session_state.current_index]
        st.subheader(f"Pregunta {st.session_state.current_index + 1} de {num_items}")

        # Progress bar
        progress_bar_value = (st.session_state.current_index + 1) / len(quiz_data)
        st.progress(progress_bar_value)


        st.title(f"{question_item['question']}")
        # st.write(question_item['information'])


        # Answer selection
        options = question_item['options']
        correct_answer = question_item['answer']

        bandera_error = False
        
        if st.session_state.answer_submitted:
            for i, option in enumerate(options):
                label = option
                if option == correct_answer:
                    st.success(f"{label} (RESPUESTA CORRECTA)")
                elif option == st.session_state.selected_option:
                    st.error(f"{label} (RESPUESTA INCORRECTA)")
                    bandera_error = True
                else:
                    st.write(label)
        else:
            for i, option in enumerate(options):
                if st.button(option, key=i, use_container_width=True):
                    st.session_state.selected_option = option
                    st.session_state.select_answer = False


        # Submission button and response logic
        if st.session_state.answer_submitted:
            if st.session_state.current_index < len(quiz_data) - 1:
                st.button('SIGUIENTE', on_click=next_question)
            else:
                tot_points = st.session_state.score / len(quiz_data) * 10
                now = datetime.now()
                elapsed_time = now - st.session_state['start_time']
                formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
                st.write(f"¡Felicidades, completaste el quiz! Tu puntaje final es: {round(tot_points,2)}")
                save_data("./content/leaderboard.csv", st.session_state['usuario'], tot_points, formatted_now, elapsed_time.total_seconds())
                st.button('SALIR', on_click=restart_quiz_without_rerun)
                #if st.button("SALIR"):
                #    restart_quiz()
                
        else:
            if st.session_state.current_index < len(quiz_data):
                st.button('ENVIAR', on_click=submit_answer)

        #Error message if no answer selected
        if st.session_state.select_answer:
            st.error("Por favor seleccione una opción", icon="🚨")
            # st.session_state.select_answer = False

        #Puntaje
        st.metric(label="PUNTAJE", value=f"{round(st.session_state.score / len(quiz_data) * 10,2)}")
        
        # Sounds
        if st.session_state.answer_submitted:
            if bandera_error:
                autoplay_audio("./sounds/buuu.m4a")
            else:
                autoplay_audio("./sounds/bien.m4a")

        st.markdown(""" ___""")

        #Timer test
        # tleft_paceholder = st.empty()
        # while True:
        #     now = datetime.now()
        #     elapsed_time_seconds = (now - st.session_state['start_time']).total_seconds()
        #     tleft_paceholder.write(f"Tiempo: {int(elapsed_time_seconds)}s")
        #     time.sleep(1)
    else:
        st.write("No hay preguntas")
        if st.button("Salir"):
            restart_quiz()



################ ADMIN ################
# Function to display the records
def display_records():
    
    for index, record in enumerate(data):
        st.write(f"**Pregunta {index + 1}**")
        st.write(f"**Pregunta:** {record['question']}")
        # st.write(f"**Info extra (opcional):** {record['information']}")
        st.write(f"**Opciones:** {', '.join(record['options'])}")
        st.write(f"**Respuesta:** {record['answer']}")
        if st.button(f"Editar pregunta {index + 1}"):
            edit_record(index)
        if st.button(f"Borrar pregunta {index + 1}"):
            delete_record(index)
        st.write("---")

# Function to edit a record
def edit_record(index):
    st.session_state['edit_index'] = index
    st.session_state['edit_mode'] = True
    st.rerun()

# Function to delete a record
def delete_record(index):
    del data[index]
    save_file(data)
    st.rerun()

# Function to add a new record
def add_record():
    new_record = {
        "question": st.text_input("Pregunta"),
        "options": st.text_input("Opciones (separar con comas)").split(","),
        "answer": st.text_input("Respuesta")
    }
    if st.button("Agregar pregunta"):
        data.append(new_record)
        save_file(data)
        st.rerun()

# Save JSON data to a file (optional)
def save_file(data):
    with open("./content/quiz_data.json", "w") as f:
        json.dump(data, f)

# Function to save edited record
def save_record(index):
    data[index] = {
        "question": st.text_input("Question", data[index]['question']),
        "options": st.text_input("Options (comma separated)", ",".join(data[index]['options'])).split(","),
        "answer": st.text_input("Answer", data[index]['answer'])
    }
    if st.button("Guardar pregunta"):
        save_file(data)
        st.session_state['edit_mode'] = False
        st.rerun()
#######################################


def reset_records():
    file_path = './content/leaderboard.csv'
    columns = ['user_email', 'total_points', 'date_responded', 'elapsed_time']
    empty_df = pd.DataFrame(columns=columns)
    empty_df.to_csv(file_path, index=False)
    restart_quiz()

def display_admin():
    if st.session_state['edit_mode']:
        save_record(st.session_state['edit_index'])
    else:
        display_records()
        st.write("### Agregar pregunta")
        add_record()
    st.divider()

    # Read the CSV file
    file_path = './content/leaderboard.csv'
    df = pd.read_csv(file_path)

    # Convert DataFrame to CSV
    csv = df.to_csv(index=False, encoding='utf-8')


    st.divider()
    st.header("Archivo de preguntas")

    json_string = json.dumps(quiz_data)

    st.download_button(
        label = "💾 Descargar archivo de preguntas",
        data=json_string,
        file_name="quiz_data.json",
        mime="application/json",
    )

    st.divider()


    # Add download button
    st.header("Resultados")
    st.download_button(
        label="🗒 Descargar resultados",
        data=csv,
        file_name='SuraQuiz-Resultados.csv',
        mime='text/csv'
    )
    if st.button("🫙 Borrar resultados"):
        st.session_state.delete_confirmation = True
    if st.session_state.delete_confirmation:
        if st.button("📍 ¿Seguro?"):
            st.session_state.delete_confirmation = False 
            reset_records()


    st.divider()
    if st.button("🔑 SALIR"):
        restart_quiz()



if nombre_usuario == "":
    
    #########################
    #         LOGIN         #
    #########################
    display_login()
    display_leaderboard()


else:

    if nombre_usuario == "sura1":
        display_admin()
    

    else:
        #########################
        #          QUIZ         #
        #########################
        display_quiz()
    


    