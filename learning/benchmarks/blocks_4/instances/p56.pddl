;; blocks=2, percentage_new_tower=10, out_folder=., instance_id=56, seed=6

(define (problem blocksworld-56)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (arm-empty)
    (clear b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on-table b2))))