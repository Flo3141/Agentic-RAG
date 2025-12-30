## 

Wir benutzen Hashes der Funktionen, um zu sehen, ob sich eien Funktion verändert hat. Inder Vektor DB benutzen wir UUID basierend auf der symbol ID der Funktionen --> die haben wir von AST.
Eine ID wird immer nur dann geupdated, wenn der dazugehörige Hash sich ändert.



RAG kann jetzt besser die Overklasse erkennen und auch zwischen den Funktionen Kontext mitnehmen --> Heißt ArithmeticOperations nicht "Calculator" --> wird oft haluziniert

Gib aber immernoch Haluzinationen / EIgeen Examples werden creaiert --> Die Examples passen oft nicht zu den Funktionen 

Kann Kontext zwischen Funktionen erkennnen --> subtract raised \_check\_limits funktion --> Ist dann auch in See also drinne

Manchaml kommt es dazu, dass als erster Einterag "Symbol" kommt, was fälschlicherweise als Finanz Symbol interpretiert wurde

Beim RAG mit Git Diff kommt es zu einer Fehlermeldung am Ende des Pushes, da das Skirpt vor dem endgültigen Pushen noch die neuen Dokumentationen hinzufügt und dann einnen neuen Push startet. Der "alte" Push Aufruf wird zur Sicherheit abgebrochen, weil es nichts mehr zu pushen gibt, weil das das Skript schon erledigt hat.

