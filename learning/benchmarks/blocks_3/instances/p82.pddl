;; blocks=3, percentage_new_tower=0, out_folder=., instance_id=82, seed=2

(define (problem blocksworld-82)
 (:domain blocksworld)
 (:objects b1 b2 b3 - object)
 (:init 
    (clear b3)
    (on b3 b1)
    (on b1 b2)
    (on-table b2))
 (:goal  (and 
    (clear b1)
    (on b1 b2)
    (on b2 b3)
    (on-table b3))))