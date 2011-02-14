#ifndef MH_DBUS_COMMON_H
#define MH_DBUS_COMMON_H

#include <glib.h>
#include <dbus/dbus-glib.h>

/* GObject class definition */
#include "mh_gobject_class.h"

#define MATAHARI_ERROR matahari_error_quark ()
enum { MATAHARI_AUTHENTICATION_ERROR, MATAHARI_NOT_IMPLEMENTED };

GQuark
matahari_error_quark (void);

gboolean
check_authorization(const gchar *action, GError** error, DBusGMethodInvocation *context);

typedef struct {
    int prop;
    gchar *name, *nick, *desc;
    GParamFlags flags;
    char type;
} Property;

gboolean
get_paramspec_from_property(Property prop, GParamSpec** spec);

int
run_dbus_server();

gboolean
matahari_get(Matahari* matahari, const char *interface, const char *name, DBusGMethodInvocation *context);

gboolean
matahari_set(Matahari *matahari, const char *interface, const char *name, GValue *value, DBusGMethodInvocation *context);

#endif
