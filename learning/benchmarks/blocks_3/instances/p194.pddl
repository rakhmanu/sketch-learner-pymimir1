;; blocks=2, percentage_new_tower=20, out_folder=., instance_id=194, seed=14

(define (problem blocksworld-194)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b1)
    (on-table b1)
    (clear b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on-table b2))))
