

(define (problem BW-rand-4)
(:domain blocksworld)
(:objects b1 b2 b3 b4  - block)
(:init
(on-table b1)
(on b2 b3)
(on b3 b4)
(on b4 b1)
(clear b2)
)
(:goal
(and
(clear b1))
)
)


