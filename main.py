import os
import asyncio
import httpx
import csv
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD PARA LA NUBE ---
# Aquí NO ponemos las llaves reales, el sistema las tomará de la "caja fuerte" de la nube
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

async def obtener_noticias_mercado(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=es&pageSize=3"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
            articulos = data.get('articles', [])
            contexto = " | ".join([a['title'] for a in articulos])
            return contexto if contexto else "Sin noticias recientes."
        except Exception:
            return "No se pudieron obtener noticias."

async def analizar_y_guardar(producto):
    noticias = await obtener_noticias_mercado(producto)
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"Analista Hedge Fund. Activo: {producto}. Noticias: {noticias}. Dame: SENTIMIENTO, ACCIÓN y POR QUÉ (15 palabras)."
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url_groq, json=payload, headers=headers)
            res_data = response.json()
            
            if 'choices' in res_data:
                analisis = res_data['choices'][0]['message']['content']
                # Guardamos en la nube para auditoría
                with open('historial_millonario.csv', mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), producto, analisis])
                return analisis
            return "Error en respuesta de IA."
        except Exception as e:
            return f"Error: {e}"

async def main():
    mis_activos = ["Bitcoin", "Oro", "Petróleo Crudo", "Nvidia", "Ethereum"]
    print("🚀 SISTEMA MILLONARIO EN LA NUBE INICIADO...")
    
    for activo in mis_activos:
        print(f"🔍 Analizando {activo}...")
        resultado = await analizar_y_guardar(activo)
        print(f"📊 {activo}: {resultado}")
        await asyncio.sleep(2) 

if __name__ == "__main__":
    asyncio.run(main())
