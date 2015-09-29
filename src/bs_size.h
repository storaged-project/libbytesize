#ifndef _BS_SIZE_H
#define _BS_SIZE_H

#include <glib.h>
#include <glib-object.h>

G_BEGIN_DECLS

#define BS_TYPE_SIZE            (bs_size_get_type())
#define BS_SIZE(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), BS_TYPE_SIZE, BSSize))
#define BS_IS_SIZE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj)), BS_TYPE_SIZE)
#define BS_SIZE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), BS_TYPE_SIZE, BSSizeClass))
#define BS_IS_SIZE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), BS_TYPE_SIZE))
#define BS_SIZE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), BS_TYPE_SIZE, BSSizeClass))

typedef struct _BSSize        BSSize;
typedef struct _BSSizeClass   BSSizeClass;
typedef struct _BSSizePrivate BSSizePrivate;

GType bs_size_get_type ();

/**
 * bs_size_new_from_bytes: (constructor)
 *
 * Creates a new #BSSize instance.
 *
 * Returns: (transfer full): a new #BSSize
 */
BSSize* bs_size_new_from_bytes (guint64 bytes);

/**
 * bs_size_new: (constructor)
 * Creates a new #BSSize instance.
 *
 * Returns: (transfer full): a new #BSSize
 */
BSSize* bs_size_new ();

guint64 bs_size_get_bytes (BSSize *size);

G_END_DECLS

#endif  /* _BS_SIZE_H */
