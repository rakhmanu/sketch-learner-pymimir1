;; blocks=2, percentage_new_tower=20, out_folder=., instance_id=190, seed=10

(define (problem blocksworld-190)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (arm-empty)
    (clear b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b1)
    (on-table b1)
    (clear b2)
    (on-table b2))))
