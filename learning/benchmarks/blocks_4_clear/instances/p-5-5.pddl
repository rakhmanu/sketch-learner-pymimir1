

(define (problem BW-rand-5)
(:domain blocksworld)
(:objects b1 b2 b3 b4 b5  - block)
(:init
(on b1 b4)
(on b2 b1)
(on-table b3)
(on b4 b5)
(on-table b5)
(clear b2)
(clear b3)
)
(:goal
(and
(clear b1))
)
)

