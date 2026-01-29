# ⚡Conciliador de Energia Inteligente 

> Uma ferramenta que transforma PDFs e imagens escaneadas em relatórios financeiros precisos usando Inteligência Artificial e Lógica Matemática.

---

##  O Problema
Processar dezenas de faturas de energia (Equatorial, Energisa, Amazonas Energia) todo mês é uma tarefa repetitiva, chata e sujeita a erros humanos. Cada concessionária tem um layout diferente, e faturas escaneadas (aquelas "xerox" tortas) são um pesadelo para ler.

##  A Solução
Desenvolvi uma **Plataforma Web (SaaS)** que automatiza 100% desse fluxo. Você arrasta os PDFs e o sistema me devolve um Excel formatado, pronto para a auditoria.

###  O que ele faz?
1.  **Leitura Universal:** Aceita tanto PDFs digitais perfeitos quanto imagens escaneadas (usando OCR Tesseract).
2.  **Identificação Automática:** Sabe sozinho se a conta é de Altamira, Coari ou Rio Branco baseada no histórico.
3.  **Visualização Interativa:** Gráficos de custo por estado e eficiência energética gerados na hora.
4.  **Exportação Bancária:** Gera um Excel (.xlsx) formatado com padrão gerencial (R$, kWh, Data).

---

##  O Diferencial: 
A grande mágica deste projeto não é apenas ler texto, é **pensar como um auditor**. O sistema possui três camadas de inteligência:

* **Nível 1 (O Leitor Rápido):** Usa Regex para extrair dados de faturas digitais limpas. É instantâneo.
* **Nível 2 (O Detetive Matemático):** Se a fatura está suja ou o OCR falha, o sistema aplica a lógica do "Sherlock". Ele varre o documento procurando números que, se divididos, resultem num preço de kWh coerente com o mercado (entre R$ 0,30 e R$ 2,50). 
    * *Exemplo:* Se ele lê R$ 5.000,00 mas não acha o consumo, ele procura matematicamente qual número no papel resulta numa tarifa real.
* **Nível 3 (A Trava de Segurança):** Se tudo falhar, ele alerta o usuário para uma conferência manual na nossa tabela interativa.

---

##  Tecnologias Usadas

O projeto foi construído com uma stack moderna de Data Science:

* **Frontend/Backend:** [Streamlit](https://streamlit.io/) (Python)
* **Processamento de Dados:** Pandas & NumPy
* **OCR (Visão Computacional):** Tesseract & PDF2Image
* **Visualização:** Plotly (Gráficos Interativos)
* **Engenharia:** Lógica customizada de validação fiscal (Python Puro)

---

##  Como Rodar Localmente

Se você quiser rodar essa aplicação na sua máquina:

1. **Clone o repositório**
   ```bash
   git clone [https://github.com/SEU-USUARIO/conciliador-basa.git](https://github.com/SEU-USUARIO/conciliador-basa.git)
   cd conciliador-basa
