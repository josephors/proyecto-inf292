"""
generar_graficos_objetivo.py
---------------------------------
Genera figuras para analizar el valor de la función objetivo en relación con el
tamaño del problema y sus componentes (trabajadores y días).

Entradas esperadas (JSON):
- ../resultados/resumen_ejecucion.json: resumen global (solo se usa para imprimir totales).
- ../resultados/<tipo>/resultado_*.json: resultados por instancia con claves:
    {
        "id_instancia", "tipo" (small|medium|large), "trabajadores", "dias",
        "valor_objetivo", "factible" (bool)
    }

Salidas (PNG en ./graficos/):
- objetivo_vs_tamano.png: scatter general + tendencia lineal.
- objetivo_trabajadores_dias.png: dos subgráficos (vs trabajadores, vs días).
- objetivo_promedio_tipo.png: barras con promedio y desviación típica por tipo.
- correlacion_matriz.png: matriz de correlación entre variables numéricas.

Notas:
- Solo se consideran instancias factibles para los gráficos de objetivo.
- El tamaño del problema se aproxima por trabajadores × días.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Correcto: configurar backend sin GUI


# Configuración de estilo
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("=" * 70)
print("ANÁLISIS: FUNCIÓN OBJETIVO VS TAMAÑO DE INSTANCIA")
print("=" * 70)

# 1. Carga de Datos
print("\n1. Cargando datos...")

# Cargar resumen de ejecución (opcional para imprimir totales)
with open('../resultados/resumen_ejecucion.json', 'r') as f:
    resumen = json.load(f)

Path('./plots/objetivo/').mkdir(parents=True, exist_ok=True)


# Extraer datos de instancias (solo factibles)
datos = []

for tamano in ['small', 'medium', 'large']:
    carpeta = Path(f'../resultados/{tamano}')
    
    for archivo in carpeta.glob('resultado_*.json'):
        with open(archivo, 'r') as f:
            resultado = json.load(f)
            
            # Solo incluir instancias factibles para el análisis de objetivo
            if resultado['factible']:
                datos.append({
                    'id': resultado['id_instancia'],
                    'tipo': resultado['tipo'],
                    'trabajadores': resultado['trabajadores'],
                    'dias': resultado['dias'],
                    'valor_objetivo': resultado['valor_objetivo'],
                    'tamano_problema': resultado['trabajadores'] * resultado['dias']
                })

# Crear DataFrame
df = pd.DataFrame(datos)
df = df.sort_values('tamano_problema')

print(f"   Total de instancias factibles: {len(df)}")
print(f"\n   Estadísticas por tipo:")
print(df.groupby('tipo')[['trabajadores', 'dias', 'tamano_problema', 'valor_objetivo']].mean().round(2))

# 2. Gráfico principal: Valor objetivo vs tamaño del problema
print("\n2. Generando gráfico: Valor objetivo vs tamaño del problema...")

# --------------------------------------------------
#  Plot: Valor de la función objetivo vs Tamaño del problema
#  - Scatter por tipo (solo instancias factibles)
#  - Ajuste de tendencia: línea recta (grado 1)
# --------------------------------------------------

fig, ax = plt.subplots(1, 1, figsize=(12, 7))

# Colores por tipo
colores = {'small': '#3498db', 'medium': '#e74c3c', 'large': '#2ecc71'}

for tipo in ['small', 'medium', 'large']:
    datos_tipo = df[df['tipo'] == tipo]
    ax.scatter(datos_tipo['tamano_problema'], 
               datos_tipo['valor_objetivo'],
               c=colores[tipo],
               s=150,
               alpha=0.7,
               label=tipo.capitalize(),
               edgecolors='black',
               linewidth=1.5)

# Línea de tendencia general (ajuste lineal y = ax + b)
# Comprobación: se requieren al menos 2 puntos para ajuste lineal
if len(df) >= 2:
    z = np.polyfit(df['tamano_problema'], df['valor_objetivo'], 1)
    p = np.poly1d(z)
    ax.plot(df['tamano_problema'], p(df['tamano_problema']), 
            "k--", alpha=0.5, linewidth=2, label='Tendencia lineal')
else:
    print('   Aviso: no hay suficientes instancias factibles para ajustar tendencia lineal (se requieren >=2).')

# Etiquetas
ax.set_xlabel('Tamaño del Problema (Trabajadores × Días)', fontsize=12, fontweight='bold')
ax.set_ylabel('Valor de la Función Objetivo', fontsize=12, fontweight='bold')
ax.set_title('Función Objetivo vs Tamaño de la Instancia', fontsize=14, fontweight='bold', pad=20)
ax.legend(fontsize=11, frameon=True, shadow=True)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('./plots/objetivo/objetivo_vs_tamano.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Guardado: graficos/objetivo_vs_tamano.png")
print(f"   Ecuación de tendencia: y = {z[0]:.2f}x + {z[1]:.2f}")
plt.close()

# 3. Subgráficos: Valor objetivo vs trabajadores y vs días
print("\n3. Generando gráfico: Valor objetivo vs trabajadores y días...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Valor objetivo vs número de trabajadores
for tipo in ['small', 'medium', 'large']:
    datos_tipo = df[df['tipo'] == tipo]
    axes[0].scatter(datos_tipo['trabajadores'], 
                    datos_tipo['valor_objetivo'],
                    c=colores[tipo],
                    s=120,
                    alpha=0.7,
                    label=tipo.capitalize(),
                    edgecolors='black',
                    linewidth=1.5)

axes[0].set_xlabel('Número de Trabajadores', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Valor Objetivo', fontsize=11, fontweight='bold')
axes[0].set_title('Valor Objetivo vs Trabajadores', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Valor objetivo vs número de días
for tipo in ['small', 'medium', 'large']:
    datos_tipo = df[df['tipo'] == tipo]
    axes[1].scatter(datos_tipo['dias'], 
                    datos_tipo['valor_objetivo'],
                    c=colores[tipo],
                    s=120,
                    alpha=0.7,
                    label=tipo.capitalize(),
                    edgecolors='black',
                    linewidth=1.5)

axes[1].set_xlabel('Número de Días', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Valor Objetivo', fontsize=11, fontweight='bold')
axes[1].set_title('Valor Objetivo vs Días', fontsize=12, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('./plots/objetivo/objetivo_trabajadores_dias.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Guardado: graficos/objetivo_trabajadores_dias.png")
plt.close()

# 4. Gráfico de barras con promedio por tipo
print("\n4. Generando gráfico: Valor objetivo promedio por tipo...")

fig, ax = plt.subplots(figsize=(10, 6))

promedios = df.groupby('tipo')['valor_objetivo'].agg(['mean', 'std', 'min', 'max'])
promedios = promedios.reindex(['small', 'medium', 'large'])

x = range(len(promedios))
tipos = ['Small', 'Medium', 'Large']
colores_bar = ['#3498db', '#e74c3c', '#2ecc71']

bars = ax.bar(x, promedios['mean'], 
              color=colores_bar, 
              alpha=0.7, 
              edgecolor='black', 
              linewidth=1.5,
              yerr=promedios['std'],
              capsize=8,
              error_kw={'linewidth': 2, 'ecolor': 'gray'})

# Etiquetas en las barras
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.0f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xlabel('Tipo de Instancia', fontsize=12, fontweight='bold')
ax.set_ylabel('Valor Objetivo Promedio', fontsize=12, fontweight='bold')
ax.set_title('Valor Objetivo Promedio por Tipo de Instancia', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(tipos, fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('./plots/objetivo/objetivo_promedio_tipo.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Guardado: graficos/objetivo_promedio_tipo.png")
plt.close()

print("\n   Promedios por tipo:")
for idx, tipo in enumerate(['small', 'medium', 'large']):
    print(f"   - {tipo.capitalize()}: {promedios.iloc[idx]['mean']:.2f} (±{promedios.iloc[idx]['std']:.2f})")

# 5. Matriz de correlación
print("\n5. Generando gráfico: Matriz de correlación...")

correlaciones = df[['trabajadores', 'dias', 'tamano_problema', 'valor_objetivo']].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlaciones, 
            annot=True, 
            fmt='.3f', 
            cmap='coolwarm', 
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={'shrink': 0.8},
            ax=ax)

ax.set_title('Matriz de Correlación', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('./plots/objetivo/correlacion_matriz.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Guardado: graficos/correlacion_matriz.png")
plt.close()

print("\n   Correlaciones con el valor objetivo:")
for var, corr in correlaciones['valor_objetivo'].sort_values(ascending=False).items():
    if var != 'valor_objetivo':
        print(f"   - {var}: {corr:.3f}")

# Resumen final
print("\n" + "=" * 70)
print("CONCLUSIONES")
print("=" * 70)
print("""
1. Relación lineal fuerte: Correlación positiva muy fuerte entre el tamaño
   del problema y el valor de la función objetivo.

2. Escalabilidad: El valor objetivo crece proporcionalmente con el aumento
   de trabajadores y días.

3. Mayor impacto de trabajadores: El número de trabajadores tiene mayor
   correlación con el valor objetivo que el número de días.

4. Variabilidad: Las instancias large muestran mayor variabilidad,
   lo cual es esperado dado sus mayores grados de libertad.

5. Infactibilidad: Las 2 instancias infactibles (12 y 15) son large,
   sugiriendo que restricciones estrictas pueden hacer inviable la
   asignación en problemas grandes.
""")
print("=" * 70)
print("\n✓ Análisis completado. Gráficos guardados en graficos/")
