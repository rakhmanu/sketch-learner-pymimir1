;; original sequence 1: (1 30 7 2 23 12 3 -32 6 8 21 31 9 -10 11 19 14 18 33 28 -29 27 24 -15 35 16 -34 26 -17 36 20 25 4 22 5 13)
;; original sequence 2: (1 34 13 24 15 10 28 9 4 7 11 17 16 19 2 36 35 20 21 -29 -25 -27 -12 -30 -18 -14 26 -6 -32 -33 -3 31 8 22 5 23)
;; simplified sequence 1: (1 30 7 2 23 12 3 -32 6 8 21 31 9 -10 11 19 38 33 28 -29 27 24 -15 35 16 -34 26 -17 36 20 25 4 37 13)
;; simplified sequence 2: (1 34 13 24 15 10 28 9 4 7 11 17 16 19 2 36 35 20 21 -29 -25 -27 -12 -30 -38 26 -6 -32 -33 -3 31 8 37 23)
;; common subsequences: (((22 5) . 37) ((14 18) . 38))
;; #safe insertions/deletions: 0
;; sequence 1 (names): ((NORMAL COX1) (NORMAL R) (NORMAL NAD4L) (NORMAL COX2) (NORMAL K) (NORMAL ATP6) (NORMAL COX3) (INVERTED S2) (NORMAL NAD3) (NORMAL NAD4) (NORMAL H) (NORMAL S1) (NORMAL NAD5) (INVERTED NAD6) (NORMAL COB) (NORMAL F) (NORMAL SUB2) (NORMAL T) (NORMAL P) (INVERTED Q) (NORMAL N) (NORMAL L1) (INVERTED A) (NORMAL W) (NORMAL C) (INVERTED V) (NORMAL M) (INVERTED D) (NORMAL Y) (NORMAL G) (NORMAL L2) (NORMAL NAD1) (NORMAL SUB1) (NORMAL RRNL))
;; sequence 2 (names): ((NORMAL COX1) (NORMAL V) (NORMAL RRNL) (NORMAL L1) (NORMAL A) (NORMAL NAD6) (NORMAL P) (NORMAL NAD5) (NORMAL NAD1) (NORMAL NAD4L) (NORMAL COB) (NORMAL D) (NORMAL C) (NORMAL F) (NORMAL COX2) (NORMAL Y) (NORMAL W) (NORMAL G) (NORMAL H) (INVERTED Q) (INVERTED L2) (INVERTED N) (INVERTED ATP6) (INVERTED R) (INVERTED SUB2) (NORMAL M) (INVERTED NAD3) (INVERTED S2) (INVERTED T) (INVERTED COX3) (NORMAL S1) (NORMAL NAD4) (NORMAL SUB1) (NORMAL K))

(DEFINE (PROBLEM PARACENTROTUS-LIVIDUS-TO-CEPAEA-NEMORALIS)
        (:DOMAIN GENOME-EDIT-DISTANCE)
        (:OBJECTS SUB2 SUB1 Y W V T S2 S1 R Q P N M L2 L1 K H G F D C A
            RRNL ATP6 COB NAD6 NAD5 NAD4 NAD4L NAD3 NAD1 COX3 COX2
            COX1)
        (:INIT (NORMAL COX1) (NORMAL R) (NORMAL NAD4L) (NORMAL COX2)
               (NORMAL K) (NORMAL ATP6) (NORMAL COX3) (INVERTED S2)
               (NORMAL NAD3) (NORMAL NAD4) (NORMAL H) (NORMAL S1)
               (NORMAL NAD5) (INVERTED NAD6) (NORMAL COB) (NORMAL F)
               (NORMAL SUB2) (NORMAL T) (NORMAL P) (INVERTED Q)
               (NORMAL N) (NORMAL L1) (INVERTED A) (NORMAL W)
               (NORMAL C) (INVERTED V) (NORMAL M) (INVERTED D)
               (NORMAL Y) (NORMAL G) (NORMAL L2) (NORMAL NAD1)
               (NORMAL SUB1) (NORMAL RRNL) (PRESENT COX1) (PRESENT R)
               (PRESENT NAD4L) (PRESENT COX2) (PRESENT K)
               (PRESENT ATP6) (PRESENT COX3) (PRESENT S2)
               (PRESENT NAD3) (PRESENT NAD4) (PRESENT H) (PRESENT S1)
               (PRESENT NAD5) (PRESENT NAD6) (PRESENT COB) (PRESENT F)
               (PRESENT SUB2) (PRESENT T) (PRESENT P) (PRESENT Q)
               (PRESENT N) (PRESENT L1) (PRESENT A) (PRESENT W)
               (PRESENT C) (PRESENT V) (PRESENT M) (PRESENT D)
               (PRESENT Y) (PRESENT G) (PRESENT L2) (PRESENT NAD1)
               (PRESENT SUB1) (PRESENT RRNL) (CW RRNL COX1)
               (CW SUB1 RRNL) (CW NAD1 SUB1) (CW L2 NAD1) (CW G L2)
               (CW Y G) (CW D Y) (CW M D) (CW V M) (CW C V) (CW W C)
               (CW A W) (CW L1 A) (CW N L1) (CW Q N) (CW P Q) (CW T P)
               (CW SUB2 T) (CW F SUB2) (CW COB F) (CW NAD6 COB)
               (CW NAD5 NAD6) (CW S1 NAD5) (CW H S1) (CW NAD4 H)
               (CW NAD3 NAD4) (CW S2 NAD3) (CW COX3 S2) (CW ATP6 COX3)
               (CW K ATP6) (CW COX2 K) (CW NAD4L COX2) (CW R NAD4L)
               (CW COX1 R) (IDLE) (= (TOTAL-COST) 0))
        (:GOAL (AND (NORMAL COX1) (NORMAL V) (NORMAL RRNL) (NORMAL L1)
                    (NORMAL A) (NORMAL NAD6) (NORMAL P) (NORMAL NAD5)
                    (NORMAL NAD1) (NORMAL NAD4L) (NORMAL COB)
                    (NORMAL D) (NORMAL C) (NORMAL F) (NORMAL COX2)
                    (NORMAL Y) (NORMAL W) (NORMAL G) (NORMAL H)
                    (INVERTED Q) (INVERTED L2) (INVERTED N)
                    (INVERTED ATP6) (INVERTED R) (INVERTED SUB2)
                    (NORMAL M) (INVERTED NAD3) (INVERTED S2)
                    (INVERTED T) (INVERTED COX3) (NORMAL S1)
                    (NORMAL NAD4) (NORMAL SUB1) (NORMAL K) (CW K COX1)
                    (CW SUB1 K) (CW NAD4 SUB1) (CW S1 NAD4)
                    (CW COX3 S1) (CW T COX3) (CW S2 T) (CW NAD3 S2)
                    (CW M NAD3) (CW SUB2 M) (CW R SUB2) (CW ATP6 R)
                    (CW N ATP6) (CW L2 N) (CW Q L2) (CW H Q) (CW G H)
                    (CW W G) (CW Y W) (CW COX2 Y) (CW F COX2) (CW C F)
                    (CW D C) (CW COB D) (CW NAD4L COB) (CW NAD1 NAD4L)
                    (CW NAD5 NAD1) (CW P NAD5) (CW NAD6 P) (CW A NAD6)
                    (CW L1 A) (CW RRNL L1) (CW V RRNL) (CW COX1 V)))
        (:METRIC MINIMIZE (TOTAL-COST)))