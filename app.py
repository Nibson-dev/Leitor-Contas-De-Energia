import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import pdfplumber
import re
import os
import pytesseract
from pdf2image import convert_from_path
import tempfile
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import time
from datetime import datetime
import glob

# ==========================================
# 🌌 CONFIGURAÇÃO GERAL
# ==========================================
st.set_page_config(page_title="BASA Enterprise", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- ASSETS (ANIMAÇÕES) ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_dash = load_lottieurl("https://lottie.host/8b724219-c7c4-4d82-9907-7c1851e44449/7zXy5Wz5w5.json")
lottie_scan = load_lottieurl("https://lottie.host/9e592750-252a-4315-9969-930490bf4468/M4jQ8Wf8W8.json")
lottie_folder = load_lottieurl("https://lottie.host/5a703716-1c25-4eb4-b9d9-937222543e5d/k2Q2y7lq3p.json") # Pasta Animada

# --- CSS SUPREMO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
    }

    /* CARDS */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    }
    
    /* INPUTS */
    .stTextInput input {
        background-color: rgba(255,255,255,0.05);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
    }

    /* BUTTONS */
    .stButton button {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    }
    
    h1, h2, h3 { color: white; }
    p { color: #A1A1AA; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 ENGINE V17 (BACKEND)
# ==========================================
DE_PARA_AGENCIAS = {
    "4988965":  {"Agencia": "Nova Marabá", "Estado": "PA", "Concessionaria": "Equatorial"},
    "23949":    {"Agencia": "Altamira", "Estado": "PA", "Concessionaria": "Equatorial"},
    "6272568":  {"Agencia": "Bacabal", "Estado": "MA", "Concessionaria": "Equatorial"},
    "4462092":  {"Agencia": "Abaetetuba", "Estado": "PA", "Concessionaria": "Equatorial"},
    "10327525": {"Agencia": "Coari", "Estado": "AM", "Concessionaria": "Amazonas Energia"},
    "1032752":  {"Agencia": "Coari", "Estado": "AM", "Concessionaria": "Amazonas Energia"},
    "447524":   {"Agencia": "Coari", "Estado": "AM", "Concessionaria": "Amazonas Energia"},
    "121842": {"Agencia": "Natividade", "Estado": "TO", "Concessionaria": "Energisa"},
    "84999":  {"Agencia": "Guajará-Mirim", "Estado": "RO", "Concessionaria": "Energisa"},
    "394924": {"Agencia": "Brasiléia", "Estado": "AC", "Concessionaria": "Energisa"},
    "426068": {"Agencia": "Cáceres", "Estado": "MT", "Concessionaria": "Energisa"},
}

def limpar_valor(texto_valor):
    if not texto_valor: return 0.0
    try: return float(re.sub(r'[^\d.,]', '', str(texto_valor)).replace('.', '').replace(',', '.'))
    except: return 0.0

def encontrar_consumo_sherlock(texto_completo, valor_fatura):
    if valor_fatura == 0: return 0.0
    padrao_numero = r"(\d{1,3}(?:\.\d{3})*,\d{2})"
    candidatos = re.findall(padrao_numero, texto_completo)
    melhor_consumo = 0.0
    for c in candidatos:
        val = limpar_valor(c)
        if val <= 10 or abs(val - valor_fatura) < 1.0: continue
        preco_calc = valor_fatura / val
        if 0.50 <= preco_calc <= 1.80:
            if val > melhor_consumo: melhor_consumo = val
    return melhor_consumo

@st.cache_data(show_spinner=False)
def processar_fatura(caminho):
    try:
        texto = ""
        usou_ocr = False
        with pdfplumber.open(caminho) as pdf:
            for p in pdf.pages[:2]: texto += p.extract_text() or ""
        
        if len(texto.strip()) < 50:
            usou_ocr = True
            try:
                imgs = convert_from_path(caminho, first_page=1, last_page=2)
                for img in imgs:
                    try: texto += pytesseract.image_to_string(img, lang='por') + "\n"
                    except: texto += pytesseract.image_to_string(img, lang='eng') + "\n"
            except: pass

        valor_total = 0.0
        gatilhos = ["Total a Pagar", "Total Consolidado", "Valor a Pagar", "TOTAL"]
        for g in gatilhos:
            m = re.search(re.escape(g) + r".{0,100}?(\d{1,3}(?:\.\d{3})*,\d{2})", texto, re.DOTALL | re.IGNORECASE)
            if m: valor_total = limpar_valor(m.group(1)); break
        
        if valor_total == 0 and usou_ocr:
            nums = re.findall(r"(\d{1,3}(?:\.\d{3})*,\d{2})", texto)
            vals = [limpar_valor(n) for n in nums if 50 < limpar_valor(n) < 2000000]
            if vals: valor_total = max(vals)

        kwh_ponta = 0.0; kwh_fponta = 0.0
        m_fp = re.search(r"(?:Fora Ponta|FP).*?([\d\.]+,\d+)\s*kWh", texto, re.IGNORECASE | re.DOTALL)
        if m_fp: kwh_fponta = limpar_valor(m_fp.group(1))
        m_p = re.search(r"(?:Ponta|Pont).*?([\d\.]+,\d+)\s*kWh", texto, re.IGNORECASE | re.DOTALL)
        if m_p: kwh_ponta = limpar_valor(m_p.group(1))
        
        kwh_total = kwh_ponta + kwh_fponta
        preco_teste = valor_total / kwh_total if kwh_total > 0 else 0
        metodo = "Leitura Automática"

        if not (0.50 <= preco_teste <= 1.80):
            kwh_sherlock = encontrar_consumo_sherlock(texto, valor_total)
            if kwh_sherlock > 0: kwh_total = kwh_sherlock; metodo = "Recuperação Matemática"
            else: kwh_total = 0.0; metodo = "FALHA - VERIFICAR"

        ref_mes = "N/A"
        match = re.search(r"\b(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)[/\s](2[456]|202[456])\b", texto, re.IGNORECASE)
        if match:
             meses = {"JAN":"01", "FEV":"02", "MAR":"03", "ABR":"04", "MAI":"05", "JUN":"06", "JUL":"07", "AGO":"08", "SET":"09", "OUT":"10", "NOV":"11", "DEZ":"12"}
             ano = match.group(2)
             if len(ano)==2: ano="20"+ano
             ref_mes = f"{meses[match.group(1).upper()]}/{ano}"
        else:
             matchs = re.findall(r"(\d{2})/(202[456])", texto)
             for m in matchs:
                 if 1 <= int(m[0]) <= 12: ref_mes = f"{m[0]}/{m[1]}"; break

        id_final = "N/A"
        info = {"Agencia": "DESCONHECIDA", "Estado": "-", "Concessionaria": "Outra"}
        numeros = re.sub(r'\D', '', texto)
        for id_db, val in DE_PARA_AGENCIAS.items():
            if id_db in numeros: info = val; id_final = id_db; break

        return {
            "UF": info['Estado'],
            "AGÊNCIA": info['Agencia'],
            "UNIDADE": id_final,
            "MÊS REF": ref_mes,
            "VALOR (R$)": valor_total,
            "CONSUMO (kWh)": kwh_total,
            "PREÇO MÉDIO": round(valor_total/kwh_total, 2) if kwh_total else 0,
            "STATUS": metodo,
            "CONCESSIONÁRIA": info['Concessionaria']
        }
    except Exception as e: return {"AGÊNCIA": "ERRO", "STATUS": str(e)}

# ==========================================
# 🌌 NAVEGAÇÃO
# ==========================================

with st.sidebar:
    if lottie_dash: st_lottie(lottie_dash, height=80)
    else: st.markdown("## ⚡ BASA AI")
    
    st.markdown("### Menu")
    selected = option_menu(
        menu_title=None,
        options=["Importar", "Dashboard", "Exportar"],
        icons=["folder-symlink", "speedometer2", "table"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#3B82F6", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px", "color": "#fafafa"},
            "nav-link-selected": {"background-color": "#3B82F6"},
        }
    )
    st.markdown("---")
    st.caption("v22.0 • Batch Processor")

if 'data' not in st.session_state: st.session_state.data = pd.DataFrame()

# --- PÁGINA: IMPORTAR (TURBO) ---
if selected == "Importar":
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.title("Central de Importação")
        st.markdown("Escolha o método de entrada para processamento.")
        
        # SELETOR DE MODO
        mode = st.radio("Fonte de Arquivos", ["📁 Pasta Local (Turbo)", "☁️ Upload Manual"], horizontal=True)
        
        files_to_process = []
        
        if mode == "📁 Pasta Local (Turbo)":
            st.info("🚀 Ideal para grandes volumes (200+ arquivos). Leitura direta do disco.")
            default_path = os.path.join(os.getcwd(), 'entradas')
            folder_path = st.text_input("Caminho da Pasta:", value=default_path)
            
            if os.path.isdir(folder_path):
                # Lista todos os PDFs
                files = glob.glob(os.path.join(folder_path, "*.pdf")) + glob.glob(os.path.join(folder_path, "*.PDF"))
                if len(files) > 0:
                    st.success(f"✅ {len(files)} faturas encontradas em '{folder_path}'")
                    files_to_process = files # Lista de caminhos (strings)
                else:
                    st.warning("Nenhum PDF encontrado nesta pasta.")
            else:
                st.error("Pasta não encontrada.")
                
        else:
            st.info("Ideal para poucos arquivos ou uso rápido.")
            uploaded = st.file_uploader("Selecione os arquivos", type="pdf", accept_multiple_files=True)
            if uploaded:
                files_to_process = uploaded # Lista de objetos UploadedFile
        
        # BOTÃO DE AÇÃO
        if len(files_to_process) > 0:
            if st.button(f"PROCESSAR {len(files_to_process)} DOCUMENTOS"):
                with st.status("Auditando em massa...", expanded=True) as status:
                    st.write("🔥 Iniciando Motor V17...")
                    bar = st.progress(0)
                    lista_res = []
                    
                    for i, file_obj in enumerate(files_to_process):
                        # Lógica diferente para Caminho vs Upload
                        if isinstance(file_obj, str):
                            # É caminho local
                            path = file_obj
                            is_temp = False
                        else:
                            # É upload (precisa de temp)
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                tmp.write(file_obj.read())
                                path = tmp.name
                            is_temp = True
                        
                        # Processa
                        res = processar_fatura(path)
                        lista_res.append(res)
                        
                        # Limpa se for temp
                        if is_temp: os.remove(path)
                        
                        bar.progress((i+1)/len(files_to_process))
                    
                    st.session_state.data = pd.DataFrame(lista_res)
                    if 'UF' in st.session_state.data.columns:
                        st.session_state.data.sort_values(['UF', 'AGÊNCIA', 'MÊS REF'], inplace=True)
                    
                    status.update(label="Concluído!", state="complete", expanded=False)
                    st.success("Auditoria Finalizada!")
                    time.sleep(1)
                    st.switch_page("app.py") # Refresh hack (opcional) ou apenas aviso
    
    with c2:
        if lottie_folder: st_lottie(lottie_folder, height=300)

# --- PÁGINA: DASHBOARD ---
elif selected == "Dashboard":
    if st.session_state.data.empty:
        st.warning("⚠️ Nenhum dado carregado.")
    else:
        df = st.session_state.data
        st.title("Analytics")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Faturas", len(df))
        k2.metric("Total Financeiro", f"R$ {df['VALOR (R$)'].sum():,.2f}")
        k3.metric("Energia Total", f"{df['CONSUMO (kWh)'].sum():,.0f} kWh")
        fails = len(df[df['STATUS'].str.contains("FALHA")])
        k4.metric("Anomalias", fails, delta="- Atenção" if fails > 0 else "OK", delta_color="inverse")
        
        st.markdown("---")
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### Custo por Agência")
            fig = px.bar(df, x="AGÊNCIA", y="VALOR (R$)", color="UF", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.markdown("#### Eficiência Energética")
            df_chart = df[df['CONSUMO (kWh)'] > 0]
            fig2 = px.scatter(df_chart, x="CONSUMO (kWh)", y="VALOR (R$)", size="VALOR (R$)", color="AGÊNCIA", template="plotly_dark")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Tabela Detalhada")
        st.dataframe(df, use_container_width=True, height=400)

# --- PÁGINA: EXPORTAR ---
elif selected == "Exportar":
    if st.session_state.data.empty:
        st.warning("⚠️ Processe arquivos primeiro.")
    else:
        st.title("Gerador de Relatórios")
        st.markdown("Valide os dados e gere a Matriz Gerencial.")
        
        df = st.session_state.data
        df_edit = st.data_editor(
            df,
            column_config={
                "VALOR (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "CONSUMO (kWh)": st.column_config.NumberColumn(format="%.2f"),
                "STATUS": st.column_config.TextColumn(help="FALHA exige correção"),
            },
            num_rows="dynamic",
            use_container_width=True,
            height=500
        )
        
        # EXPORT MATRIZ LOGIC
        from io import BytesIO
        df_pivot = df_edit.copy()
        df_pivot['DATA_SORT'] = pd.to_datetime(df_pivot['MÊS REF'], format='%m/%Y', errors='coerce')
        
        df_matrix = df_pivot.pivot_table(
            index=['UF', 'AGÊNCIA', 'UNIDADE'], 
            columns='DATA_SORT', 
            values=['CONSUMO (kWh)', 'VALOR (R$)'],
            aggfunc='sum'
        ).fillna(0)
        df_matrix = df_matrix.swaplevel(0, 1, axis=1).sort_index(axis=1)
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_matrix.to_excel(writer, sheet_name="Matriz", startrow=3)
            wb = writer.book
            ws = writer.sheets['Matriz']
            
            header_fmt = wb.add_format({'bold': True, 'fg_color': '#111827', 'font_color': 'white', 'align': 'center', 'border': 1})
            sub_fmt = wb.add_format({'bold': True, 'fg_color': '#374151', 'font_color': 'white', 'align': 'center', 'border': 1, 'font_size': 9})
            money_fmt = wb.add_format({'num_format': 'R$ #,##0.00', 'border': 1})
            kwh_fmt = wb.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'center'})
            red_bg = wb.add_format({'bg_color': '#FECACA', 'font_color': '#991B1B'})
            
            ws.merge_range('A1:Z1', "RELATÓRIO DE AUDITORIA MENSAL - BASA", wb.add_format({'bold': True, 'font_size': 14, 'align': 'center'}))
            
            dates = sorted(df_pivot['DATA_SORT'].dropna().unique())
            col_idx = 3
            meses_pt = {1:'JAN', 2:'FEV', 3:'MAR', 4:'ABR', 5:'MAI', 6:'JUN', 7:'JUL', 8:'AGO', 9:'SET', 10:'OUT', 11:'NOV', 12:'DEZ'}
            
            for dt in dates:
                d = pd.to_datetime(dt)
                head = f"{meses_pt[d.month]} {d.year}"
                ws.merge_range(2, col_idx, 2, col_idx+1, head, header_fmt)
                ws.write(3, col_idx, "kWh", sub_fmt)
                ws.write(3, col_idx+1, "R$", sub_fmt)
                ws.set_column(col_idx, col_idx, 12, kwh_fmt)
                ws.set_column(col_idx+1, col_idx+1, 15, money_fmt)
                
                col_let = chr(ord('A') + col_idx)
                ws.conditional_format(f'{col_let}5:{col_let}100', {'type': 'cell', 'criteria': '=', 'value': 0, 'format': red_bg})
                col_idx += 2
            
            ws.set_column('A:A', 6); ws.set_column('B:B', 25); ws.set_column('C:C', 20)

        st.download_button(
            label="📥 BAIXAR MATRIZ (.XLSX)",
            data=buffer.getvalue(),
            file_name="Matriz_Energia_BASA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )