;; blocks=5, percentage_new_tower=20, out_folder=., instance_id=557, seed=17

(define (problem blocksworld-557)
 (:domain blocksworld)
 (:objects b1 b2 b3 b4 b5 - object)
 (:init 
    (clear b1)
    (on b1 b3)
    (on-table b3)
    (clear b5)
    (on b5 b4)
    (on b4 b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on b1 b4)
    (on b4 b5)
    (on b5 b3)
    (on b3 b2)
    (on-table b2))))
