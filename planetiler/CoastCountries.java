import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.Planetiler;
import com.onthegomap.planetiler.Profile;
import com.onthegomap.planetiler.config.Arguments;
import com.onthegomap.planetiler.reader.SourceFeature;

import java.nio.file.Path;
import java.util.Set;

public class CoastCountries implements Profile {

  /*
   * ============================================================
   * NATURAL EARTH TABLES
   * ============================================================
   *
   * Utilitzem el mateix:
   *
   * data/sources/natural_earth_vector.sqlite.zip
   *
   * i seleccionem explícitament només les taules que volem.
   */

  private static final Set<String> LAND_TABLES = Set.of(
      "ne_110m_land",
      "ne_50m_land",
      "ne_10m_land"
  );

  private static final Set<String> COASTLINE_TABLES = Set.of(
      "ne_110m_coastline",
      "ne_50m_coastline",
      "ne_10m_coastline"
  );

  private static final Set<String> BOUNDARY_TABLES = Set.of(
      "ne_110m_admin_0_boundary_lines_land",
      "ne_50m_admin_0_boundary_lines_land",
      "ne_10m_admin_0_boundary_lines_land"
  );

  /*
   * Admin-1 mundial.
   *
   * Natural Earth té cobertura mundial detallada a 10m.
   */
  private static final String ADMIN1_TABLE =
      "ne_10m_admin_1_states_provinces";

  private static final String ADMIN1_LABEL_TABLE =
      "ne_10m_admin_1_label_points";


  @Override
  public void processFeature(
      SourceFeature source,
      FeatureCollector features
  ) {

    String table = source.getSourceLayer();


    /*
     * ============================================================
     * LAND
     * ============================================================
     */

    if (LAND_TABLES.contains(table) && source.canBePolygon()) {

      if (table.equals("ne_110m_land")) {

        features.polygon("land")
            .setMinZoom(0)
            .setMaxZoom(3);

      } else if (table.equals("ne_50m_land")) {

        features.polygon("land")
            .setMinZoom(4)
            .setMaxZoom(5);

      } else if (table.equals("ne_10m_land")) {

        features.polygon("land")
            .setMinZoom(6)
            .setMaxZoom(7);
      }

      return;
    }


    /*
     * ============================================================
     * COASTLINE
     * ============================================================
     */

    if (COASTLINE_TABLES.contains(table) && source.canBeLine()) {

      if (table.equals("ne_110m_coastline")) {

        features.line("coastline")
            .setMinZoom(0)
            .setMaxZoom(3);

      } else if (table.equals("ne_50m_coastline")) {

        features.line("coastline")
            .setMinZoom(4)
            .setMaxZoom(5);

      } else if (table.equals("ne_10m_coastline")) {

        features.line("coastline")
            .setMinZoom(6)
            .setMaxZoom(7);
      }

      return;
    }


    /*
     * ============================================================
     * ADMIN-0 COUNTRY BOUNDARIES
     * ============================================================
     */

    if (BOUNDARY_TABLES.contains(table) && source.canBeLine()) {

      if (table.equals("ne_110m_admin_0_boundary_lines_land")) {

        features.line("boundary")
            .setMinZoom(0)
            .setMaxZoom(3);

      } else if (table.equals("ne_50m_admin_0_boundary_lines_land")) {

        features.line("boundary")
            .setMinZoom(4)
            .setMaxZoom(5);

      } else if (table.equals("ne_10m_admin_0_boundary_lines_land")) {

        features.line("boundary")
            .setMinZoom(6)
            .setMaxZoom(7);
      }

      return;
    }


    /*
     * ============================================================
     * ADMIN-1 REGIONS / STATES / PROVINCES
     * ============================================================
     *
     * Geometry:
     *   polygon
     *
     * Attribute:
     *   name
     *
     * Zoom:
     *   z4-z7
     */

    if (ADMIN1_TABLE.equals(table) && source.canBePolygon()) {

      String name = String.valueOf(source.getTag("name"));

      features.polygon("admin1")
          .setMinZoom(4)
          .setMaxZoom(7)
          .setAttr("name", name);

      return;
    }


    /*
     * ============================================================
     * ADMIN-1 LABEL POINTS
     * ============================================================
     *
     * Punts preparats per Natural Earth per col·locar
     * el nom de cada regió al mapa.
     *
     * La capa resultant serà:
     *
     *   admin1_label
     *
     * amb:
     *
     *   name
     *
     * com a atribut.
     */

    if (ADMIN1_LABEL_TABLE.equals(table) && source.isPoint()) {

      String name = String.valueOf(source.getTag("name"));

      features.point("admin1_label")
          .setMinZoom(5)
          .setMaxZoom(7)
          .setAttr("name", name);

      return;
    }
  }


  /*
   * ============================================================
   * PROFILE INFORMATION
   * ============================================================
   */

  @Override
  public String name() {
    return "World land, coastline, countries and regions";
  }


  @Override
  public String description() {
    return """
        Natural Earth world map containing:
        land,
        coastline,
        country boundaries,
        first-level administrative boundaries,
        and region names.
        """;
  }


  @Override
  public String attribution() {
    return "Natural Earth";
  }


  /*
   * ============================================================
   * MAIN
   * ============================================================
   */

  public static void main(String[] args) {

    Arguments arguments = Arguments.fromArgs(args);

    Planetiler.create(arguments)

        /*
         * Mateix fitxer Natural Earth que ja tens.
         */
        .addNaturalEarthSource(
            "natural_earth",
            Path.of(
                "data",
                "sources",
                "natural_earth_vector.sqlite.zip"
            )
        )

        /*
         * Fitxer MBTiles de sortida.
         */
        .overwriteOutput(
            Path.of("world.mbtiles")
        )

        .setProfile(
            new CoastCountries()
        )

        .run();
  }
}
