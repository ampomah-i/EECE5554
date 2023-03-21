
(cl:in-package :asdf)

(defsystem "sensor_stack-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :sensor_msgs-msg
               :std_msgs-msg
)
  :components ((:file "_package")
    (:file "Vectornav" :depends-on ("_package_Vectornav"))
    (:file "_package_Vectornav" :depends-on ("_package"))
    (:file "gnss_msg" :depends-on ("_package_gnss_msg"))
    (:file "_package_gnss_msg" :depends-on ("_package"))
  ))