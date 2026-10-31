---- MODULE GenieModes ----
VARIABLES named, flash, standard
vars == <<named, flash, standard>>

Init == named \in BOOLEAN /\ flash = "asked" /\ standard = "asked"

FlashQueries == flash = "asked" /\ flash' = "oneQuery" /\ UNCHANGED <<named, standard>>
FlashHeadline == flash = "oneQuery" /\ ~named /\ flash' = "fell" /\ UNCHANGED <<named, standard>>
FlashPerDay == flash = "oneQuery" /\ named /\ flash' = "rose" /\ UNCHANGED <<named, standard>>

StdChecksDates == standard = "asked" /\ standard' = "checksDates" /\ UNCHANGED <<named, flash>>
StdFindsCutoff == standard = "checksDates" /\ standard' = "cutoff" /\ UNCHANGED <<named, flash>>
StdPerDay == standard = "cutoff" /\ standard' = "perDay" /\ UNCHANGED <<named, flash>>
StdAnswers == standard = "perDay" /\ standard' = "rose" /\ UNCHANGED <<named, flash>>

Done == flash \in {"fell", "rose"} /\ standard = "rose" /\ UNCHANGED vars

Next == FlashQueries \/ FlashHeadline \/ FlashPerDay \/ StdChecksDates \/ StdFindsCutoff \/ StdPerDay \/ StdAnswers \/ Done

Spec == Init /\ [][Next]_vars

AnswerIsRight == flash # "fell" /\ standard # "fell"
====
