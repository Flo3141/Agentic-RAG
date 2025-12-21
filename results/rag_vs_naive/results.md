## 

Wir benutzen Hashes der Funktionen, um zu sehen, ob sich eien Funktion verändert hat. Inder Vektor DB benutzen wir UUID basierend auf der symbol ID der Funktionen --> die haben wir von AST.
Eine ID wird immer nur dann geupdated, wenn der dazugehörige Hash sich ändert.



RAG kann jetzt besser die Overklasse erkennen und auch zwischen den Funktionen Kontext mitnehmen --> Heißt ArithmeticOperations nicht "Calculator" --> wird oft haluziniert

Gib aber immernoch Haluzinationen / EIgeen Examples werden creaiert --> Die Examples passen oft nicht zu den Funktionen 

Kann Kontext zwischen Funktionen erkennnen --> subtract raised \_check\_limits funktion --> Ist dann auch in See also drinne

