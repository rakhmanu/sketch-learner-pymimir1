(define (problem p01)
  (:domain ulzhal)
(:objects 
      down - direction 
      left - direction 
      right - direction 
      up - direction 
      robot - thing 
      block01 - thing 
      pos0 - location
      pos1 - location
      pos2 - location
      pos3 - location
)
 (:init
   (at robot pos1)
   (at block01 pos0)
   (clear pos2)
   (clear pos3)

   (is-goal pos2)
   (is-nongoal pos0)
   (is-nongoal pos1)
   (is-nongoal pos3)

   (is-agent robot)
   (is-block block01)
   (move-dir pos0 pos1 down)
   (move-dir pos1 pos0 up)
   (move-dir pos1 pos2 down)
   (move-dir pos2 pos1 up)
   (move-dir pos2 pos3 down)
   (move-dir pos3 pos2 up)
 )
 (:goal (and (at-goal block01) ))
)