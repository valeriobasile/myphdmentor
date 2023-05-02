# myphdmentor

Script per l'algoritmo di matching del progetto MyPhDMentor.

Bisogna scaricare le risposte manualmente come CSV e richiamarlo come argomento dello script parse.py:

    $ python src/main.py CSV_SCARICATO_DA_GOOGLE_DRIVE

Lo script ha bisogno di pandas (per leggere il csv), numpy (per i vettori), e scipy (per la weighted cosine similarity e l'algoritmo lineare). 

I pesi per i fattori sono modificabili dal file config/weights.json

L'output è costituito da un file CSV *output/matching.csv* con due colonne (*mentee* e *mentor*) contenenti rispettivamente le email delle due persone accoppiate dall'algoritmo.
 
