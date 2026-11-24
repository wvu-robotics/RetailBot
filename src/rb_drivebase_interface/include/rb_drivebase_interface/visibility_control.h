#ifndef RB_DRIVEBASE_INTERFACE__VISIBILITY_CONTROL_H_
#define RB_DRIVEBASE_INTERFACE__VISIBILITY_CONTROL_H_

// This logic was borrowed (then namespaced) from the examples on the gcc wiki:
//     https://gcc.gnu.org/wiki/Visibility

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define RB_DRIVEBASE_INTERFACE_EXPORT __attribute__ ((dllexport))
    #define RB_DRIVEBASE_INTERFACE_IMPORT __attribute__ ((dllimport))
  #else
    #define RB_DRIVEBASE_INTERFACE_EXPORT __declspec(dllexport)
    #define RB_DRIVEBASE_INTERFACE_IMPORT __declspec(dllimport)
  #endif
  #ifdef RB_DRIVEBASE_INTERFACE_BUILDING_LIBRARY
    #define RB_DRIVEBASE_INTERFACE_PUBLIC RB_DRIVEBASE_INTERFACE_EXPORT
  #else
    #define RB_DRIVEBASE_INTERFACE_PUBLIC RB_DRIVEBASE_INTERFACE_IMPORT
  #endif
  #define RB_DRIVEBASE_INTERFACE_PUBLIC_TYPE RB_DRIVEBASE_INTERFACE_PUBLIC
  #define RB_DRIVEBASE_INTERFACE_LOCAL
#else
  #define RB_DRIVEBASE_INTERFACE_EXPORT __attribute__ ((visibility("default")))
  #define RB_DRIVEBASE_INTERFACE_IMPORT
  #if __GNUC__ >= 4
    #define RB_DRIVEBASE_INTERFACE_PUBLIC __attribute__ ((visibility("default")))
    #define RB_DRIVEBASE_INTERFACE_LOCAL  __attribute__ ((visibility("hidden")))
  #else
    #define RB_DRIVEBASE_INTERFACE_PUBLIC
    #define RB_DRIVEBASE_INTERFACE_LOCAL
  #endif
  #define RB_DRIVEBASE_INTERFACE_PUBLIC_TYPE
#endif

#endif  // RB_DRIVEBASE_INTERFACE__VISIBILITY_CONTROL_H_
