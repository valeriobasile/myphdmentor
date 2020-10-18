# myphdmentor

Script per l'algoritmo di matching del progetto MyPhDMentor.

Bisogna scaricare le risposte manualmente come CSV e richiamarlo come argomento dello script parse.py:

    $ ./matching.py CSV_SCARICATO_DA_GOOGLE_DRIVE

Lo script ha bisogno di pandas (per leggere il csv), numpy (per i vettori), e scipy (per la weighted cosine similarity e l'algoritmo lineare). 

I pesi per i fattori sono modificabili dal file weights.json

L'output è costituito da due file CSV rispettivamente per i due livelli di matching:

 * *matching_1.csv*: matching tra master student e PhD student
 * *matching_2.csv*: matching tra PhD student e PhD graduate
 
