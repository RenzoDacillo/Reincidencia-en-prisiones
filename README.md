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

### Dataset
<div align="justify">
Obtenido del Sistema de Microdatos de la INEI (Instituto Nacional de Estadística e Informática) mediante el siguiente link: https://proyectos.inei.gob.pe/microdatos/ 
dentro de la encuesta de CENSO NACIONAL DE POBLACIÓN PENITENCIARIA en el año 2016.
Los datos de los internos se obtuvieron mediante una cédula censal en donde se recopilaron datos cuantitativos y cualitativos de 76619 reclusos.

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

### Predicción de reincidencia en las prisiones del Perú
