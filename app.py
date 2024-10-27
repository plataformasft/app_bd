import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración de credenciales para BigQuery
credentials_info = json.loads(os.getenv("GCP_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# ID de la tabla
table_id = "allware-387902.MIA_support_tickets.support_data"

# Función para obtener el último Ticket ID y sumarle uno
def generar_ticket_id():
    query = f"SELECT MAX(`Ticket ID`) as max_id FROM `{table_id}`"
    query_job = client.query(query)
    result = query_job.result()
    max_id = result.to_dataframe()['max_id'][0]
    return (max_id + 1) if max_id is not None else 1

# Función para enviar un correo electrónico
def enviar_correo(ticket_id, nombre, email, producto, asunto, descripcion):
    remitente = "brunodonayredonayre@gmail.com"  # Reemplaza con tu correo
    destinatarios = ["brunodonayredonayre@gmail.com", "plataformas@vitapro.com.pe"]
    contraseña = "Demian980733753"  # Reemplaza con tu contraseña o contraseña de aplicación

    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = ", ".join(destinatarios)
    mensaje["Subject"] = f"Nueva Solicitud de Soporte: Ticket ID {ticket_id}"

    # Cuerpo del correo
    cuerpo = f"""
    Nueva solicitud de soporte ha sido registrada:
    - Ticket ID: {ticket_id}
    - Nombre del Cliente: {nombre}
    - Email: {email}
    - Producto: {producto}
    - Asunto: {asunto}
    - Descripción: {descripcion}
    """
    mensaje.attach(MIMEText(cuerpo, "plain"))

    # Configuración SMTP
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.sendmail(remitente, destinatarios, mensaje.as_string())
        servidor.quit()
        st.info("Correo enviado correctamente.")
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")

# Opciones predefinidas
productos = ["Producto A", "Producto B", "Producto C"]
asuntos = ["Soporte técnico", "Consulta de producto", "Devolución", "Otro"]
generos = ["Masculino", "Femenino", "No especificar"]

# Streamlit UI para crear un nuevo ticket
st.markdown("<h1 style='display: inline;'>Portal de Solicitudes de Soporte</h1> <img src='imagen.png' style='height: 50px; display: inline;'>", unsafe_allow_html=True)

st.subheader("Ingrese su solicitud de soporte")
nombre = st.text_input("Nombre del cliente")
genero = st.selectbox("Género", generos)
email = st.text_input("Correo electrónico")
edad = st.number_input("Edad del cliente", min_value=0, step=1)
producto = st.selectbox("Producto comprado", productos)
fecha_compra = st.date_input("Fecha de compra")
asunto = st.selectbox("Asunto del ticket", asuntos)
descripcion = st.text_area("Descripción de la solicitud")

# Botón para enviar la solicitud
if st.button("Enviar solicitud"):
    if nombre and email and producto and asunto and descripcion:
        # Genera el Ticket ID automáticamente
        ticket_id = generar_ticket_id()
        
        # Inserta la solicitud en BigQuery
        rows_to_insert = [
            {
                "Ticket ID": ticket_id,
                "Customer Name": nombre,
                "Gender": genero,
                "Customer Email": email,
                "Customer Age": edad,
                "Product Purchased": producto,
                "Date of Purchase": fecha_compra.strftime("%Y-%m-%d"),
                "Ticket Subject": asunto,
                "Ticket Description": descripcion
            }
        ]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)

        if errors == []:
            st.success(f"Solicitud enviada exitosamente. Su Ticket ID es: {ticket_id}")
            # Enviar un correo con los detalles de la solicitud
            enviar_correo(ticket_id, nombre, email, producto, asunto, descripcion)
        else:
            st.error(f"Ocurrió un error al enviar la solicitud: {errors}")
    else:
        st.warning("Por favor complete todos los campos requeridos antes de enviar.")


