;; blocks=4, percentage_new_tower=0, out_folder=., instance_id=370, seed=10

(define (problem blocksworld-370)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 - object)
 (:init 
    (arm-empty)
    (clear b3)
    (on b3 b4)
    (on b4 b2)
    (on b2 b1)
    (on-table b1))
 (:goal  (and 
    (clear b3)
    (on b3 b4)
    (on b4 b2)
    (on b2 b1)
    (on-table b1))))
