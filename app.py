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
    contraseña = "Demian940407430"  # Reemplaza con tu contraseña o contraseña de aplicación

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
productos = [
    "GoPro Hero", "LG Smart TV", "Dell XPS", "Microsoft Office",
    "Autodesk AutoCAD", "Microsoft Surface", "Philips Hue Lights",
    "Fitbit Versa Smartwatch", "Dyson Vacuum Cleaner", "Nintendo Switch",
    "Microsoft Xbox Controller", "Nintendo Switch Pro Controller",
    "Nest Thermostat", "Sony PlayStation", "GoPro Action Camera",
    "Xbox", "LG Washing Machine", "Canon EOS", "HP Pavilion",
    "Amazon Kindle", "Lenovo ThinkPad", "Fitbit Charge", "Adobe Photoshop",
    "Google Pixel", "Amazon Echo", "PlayStation", "Samsung Galaxy",
    "iPhone", "LG OLED", "Sony Xperia", "Apple AirPods",
    "Sony 4K HDR TV", "Canon DSLR Camera", "Roomba Robot Vacuum",
    "Nikon D", "Bose QuietComfort", "Samsung Soundbar", "Asus ROG",
    "Bose SoundLink Speaker", "Google Nest", "Garmin Forerunner", "MacBook Pro"
]

asuntos = [
    "Product setup", "Peripheral compatibility", "Network problem",
    "Account access", "Data loss", "Payment issue", "Refund request",
    "Battery life", "Installation support", "Software bug", "Hardware issue",
    "Product recommendation", "Delivery problem", "Display issue",
    "Cancellation request", "Product compatibility"
]

tipos = [
    "Technical issue", "Billing inquiry", "Cancellation request",
    "Product inquiry", "Refund request"
]

generos = ["Masculino", "Femenino", "No especificar"]

# Streamlit UI para crear un nuevo ticket
st.markdown("<h1 style='display: inline;'>Portal de Solicitudes de Soporte</h1> ", unsafe_allow_html=True)

st.subheader("Ingrese su solicitud de soporte")
nombre = st.text_input("Nombre del cliente")
genero = st.selectbox("Género", generos)
email = st.text_input("Correo electrónico")
edad = st.number_input("Edad del cliente", min_value=0, step=1)
producto = st.selectbox("Producto comprado", productos)
fecha_compra = st.date_input("Fecha de compra")
asunto = st.selectbox("Asunto del ticket", asuntos)
descripcion = st.text_area("Descripción de la solicitud")

# Agregar Ticket Status con valor por defecto
ticket_status = "Pending Customer Response"  # Valor por defecto para Ticket Status


# Botón para enviar la solicitud
if st.button("Enviar solicitud"):
    # Verifica cada campo y muestra un mensaje específico si no está completado
    if not nombre:
        st.warning("Por favor, ingrese el nombre del cliente.")
    elif not email:
        st.warning("Por favor, ingrese el correo electrónico.")
    elif not producto:
        st.warning("Por favor, seleccione un producto comprado.")
    elif not asunto:
        st.warning("Por favor, seleccione un asunto del ticket.")
    elif not descripcion:
        st.warning("Por favor, ingrese la descripción de la solicitud.")
    else:
        # Genera el Ticket ID automáticamente
        ticket_id = generar_ticket_id()
        
        # Asegúrate de que los tipos de datos sean correctos
        rows_to_insert = [
            {
                "Ticket ID": int(ticket_id),  
                "Customer Name": str(nombre),
                "Customer Gender": str(genero),
                "Customer Email": str(email),
                "Customer Age": int(edad),
                "Product Purchased": str(producto),
                "Date of Purchase": fecha_compra.strftime("%Y-%m-%d"),  
                "Ticket Subject": str(asunto),
                "Ticket Type": str(tipo),  # Agregamos el Ticket Type
                "Ticket Description": str(descripcion) ,
                "Ticket Status": ticket_status  # Añadir el Ticket Status

            }
        ]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)

        if errors == []:
            st.success(f"Solicitud enviada exitosamente. Su Ticket ID es: {ticket_id}")
            # Enviar un correo con los detalles de la solicitud
            enviar_correo(ticket_id, nombre, email, producto, asunto, descripcion)
        else:
            st.error(f"Ocurrió un error al enviar la solicitud: {errors}")


