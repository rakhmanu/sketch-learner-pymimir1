

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5  - block)
(:init
(on-table b1)
(on-table b2)
(on b3 b4)
(on b4 b2)
(on b5 b3)
(clear b1)
(clear b5)
)
(:goal
(and
(on b1 b2)
(on b3 b1)
(on b5 b3))
)
)

