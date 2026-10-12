# Reincidencia-en-prisiones
Tarea académica, curso de inteligencia artificial aplicada 2026-2 (1INF62-1081), grupo 3
## Integrantes
* Renzo Dacillo
* Pierre Lavergne
* Luis Alberto Carrasco
## Descripción del proyecto
###  Problema
<div align="justify">
  
 Existe una sobrepoblación en las cárceles del Perú del 150% según estadísticas del INPE (febrero, 2026). Además, desde febrero del 2025 hasta febrero del 2026, hubo un crecimiento del 3.9% (3,952 internos) en la cantidad de internos. La propuesta busca, a partir de un dataset de la INEI, **predecir si un interno sentenciado es reincidente**. De esta manera, se puede prever la cantidad de vacantes que las nuevas cárceles necesitarían si es que son construidas, emplear métodos distintos de resocialización o hacer un seguimiento de los individuos para tomar medidas que eviten su reincidencia.
</div>

Bibliografía: INPE (2026). Informe estadístico febrero 2026. Recuperado de: https://siep.inpe.gob.pe/Archivos/2026/Informes%20estadisticos/informe_estadistico_febrero_2026.pdf 

### Objetivo
Debido a esta problemática, el objetivo del presente proyecto es:
>Realizar un modelo de IA para predecir la reincidencia de reclusos en las prisiones del Perú

### Dataset
<div align="justify">
Obtenido del Sistema de Microdatos de la INEI (Instituto Nacional de Estadística e Informática) mediante el siguiente link: https://proyectos.inei.gob.pe/microdatos/ 
dentro de la encuesta de CENSO NACIONAL DE POBLACIÓN PENITENCIARIA en el año 2016.
Los datos de los internos se obtuvieron mediante una cédula censal en donde se recopilaron datos cuantitativos y cualitativos de 75963 reclusos.

<p align="center">
<img width="350" height="350" alt="Cedula Sensal" src="https://github.com/user-attachments/assets/4ade8b1f-3fe8-4990-8c98-044ad886840b" /> 
<br>
Cédula sensal
</p>

El dataset obtenido se ha dividido en 5 bases de datos, cada uno con su cantidad determinada de features (columnas):
* 512-Modulo860
* 512-Modulo861
* 512-Modulo862
* 512-Modulo863
* 512-Modulo864

Como las bases de datos se encontraban en formato .sav, se los tuvo que transformar a archivos .csv, estos se encuentran en la carpeta **/data/raw** del presente repositorio.
</div>

### Predicción de reincidencia en las prisiones del Perú (Metodología)
<div align="justify">
  
En primer lugar, se realiza un análisis exploratorio de datos (EDA) con el fin de seleccionar los features relevantes para el objetivo y entender la relación entre ellos, el significado de cada feature se muestra en los diccionarios de las bases de datos pues están representadas con un código en la tablas .csv. Los features se limitaran a reclusos sentenciados, por otro lado, el target es una variable booleana llamada **P220** dentro del **módulo 862**, en donde se le pregunta al interno:
  
>SIN TOMAR EN CUENTA LA SENTENCIA QUE ACTUALMENTE CUMPLE: ¿EN ALGUNA OTRA OCASIÓN LO HABÍAN SENTENCIADO O PROCESADO A PENA EFECTIVA POR ALGÚN OTRO DELITO?

En este caso, se trata de una respuesta cerrada y por lo tanto, booleana. Luego de examinar el dataset, se procederá a eliminar features que posean múltiples valores nulos, generar imputaciones y realizar técnicas para mejorar el balanceo entre las clases reincidente y no reincidente. Se entrenará el modelo y se evaluará con las métricas necesarias. La metodología del entrenamiento será influenciada por los papers que se muestran en la carpeta **/papers**.   


### Propuesta de modelos 
***Regresión logística**: 
Es el estándar de comparación, entregando coeficientes y ratios, entrena rápido con decenas de miles de filas. Nos va a permitir decidir que factores aumentan la probabilidad de ser reincidente, sin embargo asume una relación lineal. 

***Regresión logística con LASSO**:
Permite hacer la selección de variables al llevar coeficientes a cero, lo cual nos ayuda cuando hay muchas columnas ya que añade una penalización basada en el valor absoluto de los coeficientes del modelo, podremos reportar qué variables sobrevivieron y cuales fueron descartadas, entre las variables correlacionadas se tienden a conservar de forma arbitraria y son sensibles por lo que es necesario hacer un escalado 

***Árbol de decisión**:
Es muy fácil de interpretar con reglas directas y claras. No necesita escalado de datos y captura relaciones no lineales. Sirve para comparar si Random Forest realmente vale la pena. Sin embargo, sufre mucho de sobreajuste (overfitting) y es inestable ante cambios pequeños en los datos.

***Random forest**:
Captura relaciones no lineales e interacciones sin especificarlas, no requiere escalar, tolera outliers y mezcla bien tipos de variables tras codificar, al dar importancia a las variables, la importancia por pureza sesga a la de alta cardinalidad sin embargo es menos interpretable que la logística y es mucho más costosa con cierto desbalance se tiende a favorecer a una clase mayoritaria.

***Kneighbors (KNN)**: 
No asume forma funcional y clasifica por similitud local, en base a los papers se recomienda para el uso del dataset actual, sin embargo es sensible a la escala ya que sufre con las dimensiones además de ser más lento al predecir y no da a interpretación ni importancia a las variables.

***Recidivism clustering Network (RCN)**: [3]
 1. Preprocessing: One-hot encoding, cálculos de transformación de unidades y años.
 2.  SMOTE (Synthetic Minority Over-sampling Technique): balancear datos
 3.  PCA (Análisis de componentes principales): reducir dimensionalidad para mejorar eficiencia en el entrenamiento
 4.  K-means: dividir en tipos de reclusos según semejanza
 5.  Entrenar red neuronal para cada clúster: De esta manera se evita generalizar y se toma cada caso de manera más individual
 6.  Evaluar modelo
 7.  Mostrar resultados (t-SNE, k-means, SHAP): SHAP para determinar qué factores contribuyeron a la predicción, mejorar interpretabilidad.

***Perceptrón Multicapa (MLP)**:
Captura patrones complejos y relaciones no lineales con capas ocultas. Permite comprobar si el modelo RCN mejora los resultados frente a una red neuronal estándar. Sin embargo, MPL es difícil de interpretar, necesita escalar los datos y requiere más tiempo y esfuerzo para el entrenamiento.
 
</div>
