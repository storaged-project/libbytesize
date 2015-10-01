#include <glib.h>
#include <glib-object.h>
#include <gmp.h>
#include <langinfo.h>

#include "bs_size.h"

#define N_(String) String

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

/* static void* realloc_old_new (void *ptr, gsize old_size __attribute__ ((unused)), gsize new_size) { */
/*     return g_try_realloc (ptr, new_size); */
/* } */

/* static void free_old (void *ptr, gsize old_size __attribute__ ((unused))) { */
/*     return g_free (ptr); */
/* } */

/* static void init (void) { */
/*     mp_set_memory_functions (g_try_malloc, realloc_old_new, free_old); */
/* } */


/***************
 * STATIC DATA *
 ***************/
static gchar const * const b_units[BS_BUNIT_UNDEF] = {N_("B"), N_("KiB"), N_("MiB"), N_("GiB"), N_("TiB"),
                                                      N_("PiB"), N_("EiB"), N_("ZiB"), N_("YiB")};

static gchar const * const d_units[BS_DUNIT_UNDEF] = {N_("B"), N_("KB"), N_("MB"), N_("GB"), N_("TB"),
                                                      N_("PB"), N_("EB"), N_("ZB"), N_("YB")};


/****************************
 * CLASS/OBJECT DEFINITIONS *
 ****************************/
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

GQuark bs_size_error_quark (void)
{
    return g_quark_from_static_string ("g-bs-size-error-quark");
}

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


/****************
 * CONSTRUCTORS *
 ****************/
BSSize* bs_size_new (void) {
    return BS_SIZE (g_object_new (BS_TYPE_SIZE, NULL));
}

BSSize* bs_size_new_from_bytes (guint64 bytes, GError **error __attribute__((unused))) {
    BSSize *ret = bs_size_new ();
    mpz_set_ui (ret->priv->bytes, bytes);
    return ret;
}

/**
 * replace_char:
 *
 * Replaces all appereances of @orig in @str with @new (in place).
 */
static gchar *replace_char (gchar *str, gchar orig, gchar new) {
    gchar *pos = str;
    if (!str)
        return str;

    for (pos=str; pos; pos++)
        *pos = *pos == orig ? new : *pos;

    return str;
}

static gboolean multiply_size_by_unit (mpf_t size, gchar *unit_str) {
    BSBUnit bunit = BS_BUNIT_UNDEF;
    BSDunit dunit = BS_DUNIT_UNDEF;
    guint64 pwr = 0;
    mpf_t dec_mul;

    for (bunit=BS_BUNIT_B; bunit < BS_BUNIT_UNDEF; bunit++)
        if (g_strcmp0 (unit_str, b_units[bunit]) == 0) {
            pwr = (guint64) bunit;
            mpf_mul_2exp (size, size, 10 * pwr);
            return TRUE;
        }

    mpf_init2 (dec_mul, BS_FLOAT_PREC_BITS);
    mpf_set_ui (dec_mul, 1000);
    for (dunit=BS_BUNIT_B; dunit < BS_DUNIT_UNDEF; dunit++)
        if (g_strcmp0 (unit_str, d_units[dunit]) == 0) {
            pwr = (guint64) dunit;
            mpf_pow_ui (dec_mul, dec_mul, pwr);
            mpf_mul (size, size, dec_mul);
            mpf_clear (dec_mul);
            return TRUE;
        }

    return FALSE;
}

BSSize* bs_size_new_from_str (const gchar *size_str, GError **error) {
    gchar const * const pattern = "(?P<numeric>  # the numeric part consists of three parts, below \n" \
                                  " (-|\\+)?     # optional sign character \n" \
                                  " (?P<base>([0-9\\.]+))         # base \n" \
                                  " (?P<exp>(e|E)(-|\\+)[0-9]+)?) # exponent \n" \
                                  "\\s*               # white space \n" \
                                  "(?P<rest>[^\\s]*$) # unit specification";
    GRegex *regex = NULL;
    gboolean success = FALSE;
    GMatchInfo *match_info = NULL;
    gchar *num_str = NULL;
    gchar *radix_char = NULL;
    gchar *loc_size_str = g_strdup (size_str);
    mpf_t size;
    gint status = 0;
    gchar *unit_str = NULL;
    BSSize *ret = NULL;

    radix_char = nl_langinfo (RADIXCHAR);
    if (g_strcmp0 (radix_char, ".") != 0)
        replace_char (loc_size_str, '.', *radix_char);

    regex = g_regex_new (pattern, G_REGEX_EXTENDED, 0, error);
    if (!regex) {
        g_free (loc_size_str);
        /* error is already populated */
        return NULL;
    }

    success = g_regex_match (regex, loc_size_str, 0, &match_info);
    if (!success) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Failed to parse size spec: %s", size_str);
        g_regex_unref (regex);
        g_match_info_free (match_info);
        g_free (loc_size_str);
        return NULL;
    }
    g_regex_unref (regex);

    num_str = g_match_info_fetch_named (match_info, "numeric");
    if (!num_str) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Failed to parse size spec: %s", size_str);
        g_regex_unref (regex);
        g_match_info_free (match_info);
        g_free (loc_size_str);
        return NULL;
    }

    mpf_init2 (size, BS_FLOAT_PREC_BITS);
    status = mpf_set_str (size, num_str, 10);
    if (status != 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Failed to parse size spec: %s", size_str);
        g_match_info_free (match_info);
        g_free (loc_size_str);
        mpf_clear (size);
        return NULL;
    }

    unit_str = g_match_info_fetch_named (match_info, "rest");
    if (unit_str && g_strcmp0 (unit_str, "") != 0) {
        g_strstrip (unit_str);
        if (!multiply_size_by_unit (size, unit_str)) {
            g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                         "Failed to recognize unit from the spec: %s", size_str);
            g_match_info_free (match_info);
            g_free (loc_size_str);
            mpf_clear (size);
            return NULL;
        }
    }

    ret = bs_size_new ();
    mpz_set_f (ret->priv->bytes, size);

    g_free (loc_size_str);
    g_match_info_free (match_info);
    mpf_clear (size);

    return ret;
}

BSSize* bs_size_new_from_size (BSSize *size, GError **error __attribute__((unused))) {
    BSSize *ret = NULL;

    ret = bs_size_new ();
    mpz_set (ret->priv->bytes, size->priv->bytes);

    return ret;
}


/*****************
 * QUERY METHODS *
 *****************/
guint64 bs_size_get_bytes (BSSize *size, GError **error) {
    if (mpz_cmp_ui (size->priv->bytes, G_MAXUINT64) > 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_OVER,
                     "The size is too big, cannot be returned as a 64bit number of bytes");
        return 0;
    }
    return (guint64) mpz_get_ui (size->priv->bytes);
}

gchar* bs_size_get_bytes_str (BSSize *size, GError **error __attribute__((unused))) {
    return mpz_get_str (NULL, 10, size->priv->bytes);
}


/***************
 * ARITHMETIC *
 ***************/
BSSize* bs_size_add (BSSize *size1, BSSize *size2) {
    BSSize *ret = bs_size_new ();
    mpz_add (ret->priv->bytes, size1->priv->bytes, size2->priv->bytes);

    return ret;
}

BSSize* bs_size_add_bytes (BSSize *size, guint64 bytes) {
    BSSize *ret = bs_size_new ();
    mpz_add_ui (ret->priv->bytes, size->priv->bytes, bytes);

    return ret;
}

BSSize* bs_size_sub (BSSize *size1, BSSize *size2) {
    BSSize *ret = bs_size_new ();
    mpz_sub (ret->priv->bytes, size1->priv->bytes, size2->priv->bytes);

    return ret;
}

BSSize* bs_size_sub_bytes (BSSize *size, guint64 bytes) {
    BSSize *ret = bs_size_new ();
    mpz_sub_ui (ret->priv->bytes, size->priv->bytes, bytes);

    return ret;
}

BSSize* bs_size_mul (BSSize *size, guint64 times) {
    BSSize *ret = bs_size_new ();
    mpz_mul_ui (ret->priv->bytes, size->priv->bytes, times);

    return ret;
}

guint64 bs_size_div (BSSize *size1, BSSize *size2, GError **error) {
    mpf_t op1, op2;
    guint64 ret = 0;

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_init2 (op2, BS_FLOAT_PREC_BITS);

    mpf_set_z (op1, size1->priv->bytes);
    mpf_set_z (op2, size2->priv->bytes);

    mpf_div (op1, op1, op2);

    if (mpf_cmp_ui (op1, G_MAXUINT64) > 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_OVER,
                     "The size is too big, cannot be returned as a 64bit number of bytes");
        mpf_clears (op1, op2, NULL);
        return 0;
    }
    ret = (guint64) mpf_get_ui (op1);

    mpf_clears (op1, op2, NULL);
    return ret;
}
