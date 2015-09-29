#include <glib.h>
#include <glib-object.h>
#include <gmp.h>

#include "bs_size.h"

/**
 * SECTION: Size
 * @title: BSSize
 * @short_description: a class facilitating work with sizes in bytes
 *
 * A #BSSize is class that facilitates work with sizes in bytes by providing
 * functions/methods that are required for parsing users input when entering
 * size, showing size in nice human-readable format, storing sizes bigger than
 * %G_MAXUINT64 and doing calculations with sizes without loss of
 * precision/information.
 */

/**
 * BSSize:
 *
 * The BSSize struct contains only private fields and should not be directly
 * accessed.
 */
struct _BSSize {
    GObject parent;
    BSSizePrivate *priv;
};

/**
 * BSSizeClass:
 * @parent_class: parent class of the #BSSizeClass
 */
struct _BSSizeClass {
    GObjectClass parent_class;
};

/**
 * BSSizePrivate:
 *
 * The BSSizePrivate struct contains only private fields and should not be directly
 * accessed.
 */
struct _BSSizePrivate {
    mpz_t bytes;
};

G_DEFINE_TYPE (BSSize, bs_size, G_TYPE_OBJECT)

static void bs_size_dispose(GObject *size);

static void bs_size_class_init (BSSizeClass *klass) {
    GObjectClass *object_class = G_OBJECT_CLASS(klass);

    object_class->dispose = bs_size_dispose;

    g_type_class_add_private(object_class, sizeof(BSSizePrivate));
}

static void bs_size_init (BSSize *self) {
    self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                             BS_TYPE_SIZE,
                                             BSSizePrivate);
    /* let's start with 64 bits of space */
    mpz_init2 (self->priv->bytes, (mp_bitcnt_t) 64);
}

static void bs_size_dispose (GObject *object) {
    BSSize *self = BS_SIZE (object);
    mpz_clear (self->priv->bytes);

    G_OBJECT_CLASS(bs_size_parent_class)->dispose (object);
}

BSSize* bs_size_new () {
    return BS_SIZE (g_object_new (BS_TYPE_SIZE, NULL));
}

BSSize* bs_size_new_from_bytes (guint64 bytes) {
    BSSize *ret = bs_size_new ();
    mpz_set_ui (ret->priv->bytes, bytes);
    return ret;
}

guint64 bs_size_get_bytes (BSSize *size) {
    return (guint64) mpz_get_ui (size->priv->bytes);
}
