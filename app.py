import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json

# Configura las credenciales
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

# Streamlit UI para crear un nuevo ticket
st.title("Portal de Solicitudes de Soporte")

st.subheader("Ingrese su solicitud de soporte")
nombre = st.text_input("Nombre del cliente")
email = st.text_input("Correo electrónico")
edad = st.number_input("Edad del cliente", min_value=0, step=1)
producto = st.text_input("Producto comprado")
fecha_compra = st.date_input("Fecha de compra")
asunto = st.text_input("Asunto del ticket")
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
                "Customer Email": email,
                "Customer Age": edad,
                "Product Purchased": producto,
                "Date of Purchase": fecha_compra.strftime("%Y-%m-%d"),
                "Ticket Subject": asunto,
                "Ticket Description": descripcion
            }
        ]
        
        # Inserta los datos en la tabla de BigQuery
        errors = client.insert_rows_json(table_id, rows_to_insert)

        # Verifica si hubo errores
        if errors == []:
            st.success(f"Solicitud enviada exitosamente. Su Ticket ID es: {ticket_id}")
        else:
            st.error(f"Ocurrió un error al enviar la solicitud: {errors}")
    else:
        st.warning("Por favor complete todos los campos requeridos antes de enviar.")
