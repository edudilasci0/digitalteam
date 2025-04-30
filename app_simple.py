import streamlit as st

st.title("Aplicación de Prueba - Team Digital")

st.write("Esta es una aplicación simple para verificar que Streamlit está funcionando correctamente.")

st.success("Si puedes ver este mensaje, la aplicación está funcionando correctamente.")

# Agregar un botón interactivo
if st.button("Haz clic aquí"):
    st.balloons()
    st.write("¡Funciona! El sistema está configurado correctamente.") 