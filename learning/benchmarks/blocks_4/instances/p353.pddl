;; blocks=3, percentage_new_tower=40, out_folder=., instance_id=353, seed=23

(define (problem blocksworld-353)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (arm-empty)
    (clear b3)
    (on-table b3)
    (clear b2)
    (on-table b2)
    (clear b1)
    (on-table b1))
 (:goal  (and 
    (clear b3)
    (on b3 b2)
    (on-table b2)
    (clear b1)
    (on-table b1))))
