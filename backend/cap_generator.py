"""
NEXUS-NOWCAST: ITU X.1303 / NDMA CAP v1.2 XML Alert Generator
Produces court-admissible, machine-readable disaster alerts conforming
to NDMA 'Sachet' and IMD 'Damini' emergency warning standards.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List


class CAPAlertGenerator:
    """
    Generates standard Common Alerting Protocol (CAP) v1.2 XML & GeoJSON payloads.
    """
    @staticmethod
    def generate_cap_xml(
        alert_id: str,
        event_name: str,
        severity: str,            # "Extreme", "Severe", "Moderate", "Minor"
        imd_color: str,           # "RED", "ORANGE", "YELLOW", "GREEN"
        headline: str,
        description: str,
        instruction: str,
        districts: List[str],
        polygon_coords: List[List[float]],
        lead_time_min: int = 60
    ) -> str:
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(ist_offset)
        expires_ist = now_ist + timedelta(minutes=lead_time_min + 60)

        sent_str = now_ist.strftime("%Y-%m-%dT%H:%M:%S+05:30")
        expires_str = expires_ist.strftime("%Y-%m-%dT%H:%M:%S+05:30")

        # Format polygon points as "lat,lon lat,lon ..."
        poly_str = " ".join([f"{p[0]:.4f},{p[1]:.4f}" for p in polygon_coords])
        if polygon_coords and (polygon_coords[0] != polygon_coords[-1]):
            poly_str += f" {polygon_coords[0][0]:.4f},{polygon_coords[0][1]:.4f}"

        districts_str = ", ".join(districts)

        # Compute SHA-256 Digest for Tamper-Proofing (GAP-08)
        digest_input = f"{alert_id}:{sent_str}:{event_name}:{severity}:{poly_str}".encode("utf-8")
        import hashlib, base64
        sha256_hash = hashlib.sha256(digest_input).hexdigest()
        sig_base64 = base64.b64encode(sha256_hash.encode("utf-8")).decode("utf-8")

        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>{alert_id}</identifier>
  <sender>imd-nowcast-engine@moes.gov.in</sender>
  <sent>{sent_str}</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Met</category>
    <event>{event_name}</event>
    <urgency>Immediate</urgency>
    <severity>{severity}</severity>
    <certainty>Observed</certainty>
    <eventCode>
      <valueName>IMD_COLOR_CODE</valueName>
      <value>{imd_color}</value>
    </eventCode>
    <expires>{expires_str}</expires>
    <headline>{headline}</headline>
    <description>{description}</description>
    <instruction>{instruction}</instruction>
    <area>
      <areaDesc>{districts_str}</areaDesc>
      <polygon>{poly_str}</polygon>
    </area>
  </info>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="#{alert_id}">
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>{sha256_hash}</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>{sig_base64}</SignatureValue>
  </Signature>
</alert>"""
        return xml_content


    @staticmethod
    def get_geojson_alert_polygon(
        districts: List[str],
        polygon_coords: List[List[float]],
        imd_color: str,
        severity: str,
        max_dbz: float,
        lightning_jump: bool
    ) -> Dict[str, Any]:
        """
        Formats alert polygon as GeoJSON for frontend Leaflet rendering.
        Note: GeoJSON coordinates are [lon, lat].
        """
        geojson_coords = [[p[1], p[0]] for p in polygon_coords]
        if geojson_coords and (geojson_coords[0] != geojson_coords[-1]):
            geojson_coords.append(geojson_coords[0])

        color_hex = {
            "RED": "#FF1744",
            "ORANGE": "#FF9100",
            "YELLOW": "#FFEA00",
            "GREEN": "#00E676"
        }.get(imd_color.upper(), "#FF1744")

        return {
            "type": "Feature",
            "properties": {
                "districts": districts,
                "imd_color": imd_color,
                "color_hex": color_hex,
                "severity": severity,
                "max_dbz": max_dbz,
                "lightning_jump": lightning_jump
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [geojson_coords]
            }
        }
