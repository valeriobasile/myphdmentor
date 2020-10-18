# myphdmentor

Script per l'algoritmo di matching del progetto MyPhDMentor.

Al momento calcola uno score di similarità tra tutte le coppie mentor-mentee che hanno risposto al questionario. Bisogna scaricare le risposte manualmente come CSV e richiamarlo come argomento dello script parse.py:

    $ ./parse.py CSV_SCARICATO_DA_GOOGLE_DRIVE

Lo script ha bisogno di pandas (per leggere il csv), numpy (per i vettori), e scipy (per la weighted cosine similarity). 

I pesi per i fattori sono modificabili dal file weights.json
