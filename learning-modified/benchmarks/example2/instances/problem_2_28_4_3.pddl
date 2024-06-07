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
      pos4 - location
      pos5 - location
      pos6 - location
      pos7 - location
      pos8 - location
      pos9 - location
      pos10 - location
      pos11 - location
)
 (:init
   (at robot pos3)
   (at block01 pos1)(at block01 pos8)
   (clear pos0)
   (clear pos2)
   (clear pos4)
   (clear pos5)
   (clear pos6)
   (clear pos7)
   (clear pos9)
   (clear pos10)
   (clear pos11)

   (is-goal pos10)
   (is-nongoal pos0)
   (is-nongoal pos1)
   (is-nongoal pos2)
   (is-nongoal pos3)
   (is-nongoal pos4)
   (is-nongoal pos5)
   (is-nongoal pos6)
   (is-nongoal pos7)
   (is-nongoal pos8)
   (is-nongoal pos9)
   (is-nongoal pos11)

   (is-agent robot)
   (is-block block01)
   (move-dir pos0 pos4 down)
   (move-dir pos0 pos1 right)
   (move-dir pos1 pos5 down)
   (move-dir pos1 pos0 left)
   (move-dir pos1 pos2 right)
   (move-dir pos2 pos6 down)
   (move-dir pos2 pos1 left)
   (move-dir pos2 pos3 right)
   (move-dir pos3 pos7 down)
   (move-dir pos3 pos2 left)
   (move-dir pos4 pos0 up)
   (move-dir pos4 pos8 down)
   (move-dir pos4 pos5 right)
   (move-dir pos5 pos1 up)
   (move-dir pos5 pos9 down)
   (move-dir pos5 pos4 left)
   (move-dir pos5 pos6 right)
   (move-dir pos6 pos2 up)
   (move-dir pos6 pos10 down)
   (move-dir pos6 pos5 left)
   (move-dir pos6 pos7 right)
   (move-dir pos7 pos3 up)
   (move-dir pos7 pos11 down)
   (move-dir pos7 pos6 left)
   (move-dir pos8 pos4 up)
   (move-dir pos8 pos9 right)
   (move-dir pos9 pos5 up)
   (move-dir pos9 pos8 left)
   (move-dir pos9 pos10 right)
   (move-dir pos10 pos6 up)
   (move-dir pos10 pos9 left)
   (move-dir pos10 pos11 right)
   (move-dir pos11 pos7 up)
   (move-dir pos11 pos10 left)
 )
 (:goal (and (at-goal block01) ))
)