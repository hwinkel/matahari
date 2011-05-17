/*
 * Copyright (C) 2010 Andrew Beekhof <andrew@beekhof.net>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

/**
 * \file
 * \brief Utilities API
 * \ingroup coreapi
 */

#ifndef __MH_UTILITIES__
#define __MH_UTILITIES__

#include "config.h"

#include <stdlib.h>
#include <sys/types.h>
#include <string.h>

extern const char *mh_uuid(void);
extern const char *mh_hostname(void);
extern void mh_abort(const char *file, const char *function, int line,
                     const char *assert_condition, int do_core, int do_fork);

#ifndef HAVE_ASPRINTF
/**
 * Custom implementation of asprintf()
 *
 * This version of asprintf() is only used when the build system doesn't find
 * asprintf() on the system.  For more information on how to use asprintf(),
 * see its man page.
 */
extern int asprintf(char **ret, const char *fmt, ...);
#endif

#define DIMOF(a)    ((int) (sizeof(a) / sizeof(0[a])))

#ifndef __GNUC__
#    define __builtin_expect(expr, result) (expr)
#endif

/* Some handy macros used by the Linux kernel */
#define __likely(expr) __builtin_expect(expr, 1)
#define __unlikely(expr) __builtin_expect(expr, 0)

#define MH_ASSERT(expr) do {                                                \
        if (__unlikely((expr) == 0)) {                                      \
            mh_abort(__FILE__, __PRETTY_FUNCTION__, __LINE__, #expr, 1, 0); \
        }                                                                   \
    } while(0)

#define MH_LOG_ASSERT(expr) do {                                            \
        if (__unlikely((expr) == FALSE)) {                                  \
            mh_abort(__FILE__, __PRETTY_FUNCTION__, __LINE__, #expr, 0, 1); \
        }                                                                   \
    } while(0)

#endif
