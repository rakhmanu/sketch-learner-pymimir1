;; blocks=2, percentage_new_tower=0, out_folder=., instance_id=44, seed=4

(define (problem blocksworld-44)
 (:domain blocksworld)
 (:objects b1 b2 - object)
 (:init 
    (clear b1)
    (on b1 b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on-table b2))))