export interface LatLng {
  lat: number;
  lng: number;
}

/** Browser geolocation as a promise, with messages a user can act on. */
export function getCurrentPosition(): Promise<LatLng> {
  return new Promise((resolve, reject) => {
    if (!("geolocation" in navigator)) {
      reject(new Error("這個瀏覽器不支援定位，請改選捷運站"));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      (err) => {
        const messages: Record<number, string> = {
          1: "沒有定位權限，請改選捷運站（或到瀏覽器設定允許定位）",
          2: "目前抓不到位置，請改選捷運站",
          3: "定位逾時，請改選捷運站",
        };
        reject(new Error(messages[err.code] ?? "定位失敗，請改選捷運站"));
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  });
}

/** Opens Google Maps walking directions (the app on phones, the site on desktop). */
export function directionsUrl(lat: number, lng: number, googlePlaceId?: string) {
  const params = new URLSearchParams({
    api: "1",
    destination: `${lat},${lng}`,
    travelmode: "walking",
  });
  if (googlePlaceId) params.set("destination_place_id", googlePlaceId);
  return `https://www.google.com/maps/dir/?${params}`;
}
