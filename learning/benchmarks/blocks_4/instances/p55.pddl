;; blocks=2, percentage_new_tower=10, out_folder=., instance_id=55, seed=5

(define (problem blocksworld-55)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (arm-empty)
    (clear b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b2)
    (on b2 b1)
    (on-table b1))))