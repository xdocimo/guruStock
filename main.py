import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from tabulate import tabulate
import numpy as np

definiciones = """
ROE (Rentabilidad sobre el Capital): Mide la capacidad de una empresa para generar beneficios a partir de los recursos propios.
FCF (Flujo de Caja Libre): Representa el efectivo generado por la empresa después de restar los gastos de capital.
DE RATIO (Ratio Deuda/Capital): Indica la proporción de deuda que tiene la empresa en comparación con su capital propio.
"""

# AGREGAR LAS EMPRESAS QUE GUSTES CON FORMATO: STOCK.BA si es bolsa bonaerense

tickers = ['MORI.BA', 'TGNO4.BA', 'COME.BA', 'YPFD.BA', 'BMA.BA', 'TECO2.BA', 'BBAR.BA', 'SUPV.BA', 'CEPU.BA', 
           'PAMP.BA', 'LOMA.BA', 'CRES.BA', 'HARG.BA', 'EDN.BA', 'ALUA.BA', 'TGSU2.BA', 'TGN.BA', 'TXAR.BA', 
           'TRAN.BA', 'MIRG.BA', 'COME.BA', 'VALO.BA', 'BYMA.BA', 'FERR.BA', 'CAPU.BA', 'SAM.BA', 'BRIO.BA', 
           'BOLT.BA', 'INTR.BA', 'CELU.BA', 'MERA.BA', 'BHIP.BA', 'CTIO.BA', 'GRIM.BA', 'LONG.BA', 'CVH.BA', 
           'IRSA.BA', 'MOLA.BA', 'IRCP.BA', 'EDV.BA', 'HAPU.BA', 'JMIN.BA', 'AUSO.BA', 'TGLT.BA', 'GCLA.BA', 
           'SEMI.BA', 'BRIO6.BA', 'INVJ.BA', 'INDU.BA', 'SAMIB.BA', 'INAG.BA', 'ESME.BA', 'BSEP.BA', 'CAPX.BA', 
           'CONA.BA', 'BULI.BA', 'TECO.BA', 'TS.BA', 'GFG.BA', 'JUNC.BA', 'TRIO.BA', 'DGCU2.BA', 'APBR.BA', 
           'FRAN.BA', 'FERRUM.BA']

hoy = datetime.today()
inicio_del_mes = hoy.replace(day=1)
inicio_ultimas_24h = hoy - timedelta(days=1)
fin_ultimas_24h = hoy

datos_mes = yf.download(tickers, start=inicio_del_mes, end=hoy)
datos_hist = yf.download(tickers, period="max")
datos_24h = yf.download(tickers, start=inicio_ultimas_24h, end=fin_ultimas_24h, interval='1h')

resultados = []

for ticker in tickers:
    accion = yf.Ticker(ticker)
    
    try:
        ratio_deuda_capital = accion.info['debtToEquity']
        flujo_caja_libre = accion.cashflow.loc['Free Cash Flow'].iloc[0]
        rentabilidad_capital = accion.info['returnOnEquity'] * 100
    except KeyError:
        continue
    
    try:
        max_mes = datos_mes['Close'][ticker].max()
        precio_actual = datos_mes['Close'][ticker].iloc[-1]
        caida_max_mes = ((max_mes - precio_actual) / max_mes) * 100 if max_mes != 0 else np.nan
        
        max_hist = datos_hist['Close'][ticker].max()
        fecha_max_hist = datos_hist['Close'][ticker].idxmax()
        caida_max_hist = ((max_hist - precio_actual) / max_hist) * 100 if max_hist != 0 else np.nan
        
        if ticker in datos_24h['Close']:
            try:
                datos_24h_precio = datos_24h['Close'][ticker]
                if len(datos_24h_precio) >= 2:
                    precio_ultimas_24h = datos_24h_precio.iloc[-1]
                    precio_anterior_24h = datos_24h_precio.iloc[0]
                    aumento_ultimas_24h = ((precio_ultimas_24h - precio_anterior_24h) / precio_anterior_24h) * 100 if precio_anterior_24h != 0 else np.nan
                    direccion_cambio = "Subió" if aumento_ultimas_24h > 0 else "Bajó" if aumento_ultimas_24h < 0 else "Sin Cambio"
                else:
                    aumento_ultimas_24h = np.nan
                    direccion_cambio = "Sin Datos"
            except IndexError:
                aumento_ultimas_24h = np.nan
                direccion_cambio = "Sin Datos"
        else:
            aumento_ultimas_24h = np.nan
            direccion_cambio = "Sin Datos"
        
        if precio_actual < max_mes:
            condicion = "Compra"
        elif precio_actual < max_hist:
            condicion = "Recomienda Histórico"
        else:
            condicion = "No Compra"
        
        if not np.isnan(aumento_ultimas_24h):
            variacion_ultimas_24h = f"{direccion_cambio} {aumento_ultimas_24h:.2f}%"
        else:
            variacion_ultimas_24h = "N/A"
        
        if ratio_deuda_capital < 1 and flujo_caja_libre > 0 and rentabilidad_capital > 15:
            solidez = "Sólida"
            razon = "- D/E, FCF +, ROE +"
        elif ratio_deuda_capital < 1 and flujo_caja_libre > 0:
            solidez = "Moderada"
            razon = "- D/E, FCF +, ROE -"
        elif ratio_deuda_capital < 1 and rentabilidad_capital > 15:
            solidez = "Moderada"
            razon = "- D/E, FCF -, ROE +"
        else:
            solidez = "Débil"
            razon = "+ D/E o FCF - o ROE -"
        
        if not (np.isnan(max_mes) or np.isnan(precio_actual) or np.isnan(caida_max_mes) or 
                np.isnan(max_hist) or np.isnan(caida_max_hist)):
            resultados.append({
                'Ticker': ticker,
                'MAX 30D': round(max_mes, 2),
                'ACTUAL': round(precio_actual, 2),
                '-MAX30D (%)': round(caida_max_mes, 2),
                'MAX HISTORIA': round(max_hist, 2),
                'FECHA MAX': fecha_max_hist.strftime('%Y-%m-%d'),
                '-MAXHISTORIA (%)': round(caida_max_hist, 2),
                'GURU': condicion,
                'VAR24HS': variacion_ultimas_24h,
                'SOL': solidez,
                'OBSV': razon
            })
    except KeyError:
        continue

df_resultados = pd.DataFrame(resultados)

print(definiciones)
print(tabulate(df_resultados, headers='keys', tablefmt='grid', showindex=False))
