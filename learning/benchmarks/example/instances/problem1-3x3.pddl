(define (problem p01) 
  (:domain ulzhal)
  (:objects
        down - direction
    	left - direction
    	right - direction
    	up - direction
    	robot - thing
    	pos-1-1 - location
    	pos-1-2 - location
    	pos-1-3 - location
    	pos-2-1 - location
    	pos-2-2 - location
    	pos-2-3 - location
    	pos-3-1 - location
    	pos-3-2 - location
    	pos-3-3 - location
    	pos-4-1 - location
    	pos-4-2 - location
    	pos-4-3 - location
    	block-01 - thing
    	
  )
  (:init 
	(at robot pos-1-2)
	(at block-01 pos-3-2)
    (clear pos-1-1)
	(clear pos-1-3)
	(clear pos-2-1)
	(clear pos-3-1)
	(clear pos-2-2)
	(clear pos-2-3)
	(clear pos-3-3)
	(is-goal pos-3-3)
	(is-nongoal pos-1-1)
	(is-nongoal pos-1-2)
	(is-nongoal pos-2-1)
	(is-nongoal pos-2-2)
	(is-nongoal pos-2-3)
	(is-nongoal pos-3-1)
	(is-nongoal pos-3-2)
	(is-nongoal pos-3-3)
	(is-agent robot)
	(is-block block-01)
	
    (move-dir pos-1-1 pos-1-2 down)
    (move-dir pos-1-1 pos-2-1 right)
    (move-dir pos-1-2 pos-2-2 right)
	(move-dir pos-1-2 pos-1-3 down)
	(move-dir pos-1-2 pos-1-1 up)
	(move-dir pos-1-3 pos-1-2 up)
	(move-dir pos-1-3 pos-2-3 right)
	(move-dir pos-2-1 pos-1-1 left)
	(move-dir pos-2-1 pos-3-1 right)
	(move-dir pos-2-1 pos-2-2 down)
	(move-dir pos-2-2 pos-3-2 right)
	(move-dir pos-2-2 pos-2-1 up)
	(move-dir pos-2-3 pos-2-2 up)
	(move-dir pos-2-3 pos-3-3 right)
	(move-dir pos-2-3 pos-1-3 left)
	(move-dir pos-2-2 pos-1-2 left)	
	(move-dir pos-2-2 pos-2-3 down)
	(move-dir pos-3-1 pos-2-1 left)
	(move-dir pos-3-1 pos-3-2 down)
	(move-dir pos-3-2 pos-2-2 left)
	(move-dir pos-3-2 pos-3-3 down)
	(move-dir pos-3-2 pos-3-1 up)
	(move-dir pos-3-3 pos-2-3 left)
	(move-dir pos-3-3 pos-3-2 up)
	
)
(:goal (and
	(at-goal block-01)))

)
