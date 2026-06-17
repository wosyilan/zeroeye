/**
 * @fileoverview Legacy HTTP and utility compatibility layer.
 *
 * This file contains the minimal set of legacy compatibility functions
 * that are still referenced by the migrated codebase. All AngularJS root
 * scope shims,  promise wrappers, , AngularJS filter
 * implementations, form validators, and directive registries have been
 * removed as part of the LEGACY cleanup (see #53).
 *
 * The only remaining exports are:
 *   -    - HTTP client used by api.ts
 *   - legacyToJson  - AngularJS JSON.stringify with undefined to null conversion
 */

/** AngularJS-compatible HTTP service using the native fetch API. */
export async function (config) {
  var url = config.url;
  if (config.params) {
    var sp = new URLSearchParams();
    for (var key in config.params) {
      if (config.params.hasOwnProperty(key)) sp.append(key, config.params[key]);
    }
    var qs = sp.toString();
    if (qs) url += (url.includes('?') ? '&' : '?') + qs;
  }

  var headers = { Accept: 'application/json, text/plain, */*' };
  for (var key in config.headers) {
    if (config.headers.hasOwnProperty(key)) headers[key] = config.headers[key];
  }
  if (config.data && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json;charset=utf-8';
  }

  var body = null;
  if (config.data !== undefined) {
    body = JSON.stringify(config.data);
  }

  var controller = new AbortController();
  var timeoutId = config.timeout ? setTimeout(function() { controller.abort(); }, config.timeout) : undefined;

  try {
    var response = await fetch(url, {
      method: config.method,
      headers: headers,
      body: body,
      signal: controller.signal,
      credentials: config.withCredentials ? 'include' : 'same-origin',
    });

    var ct = response.headers.get('content-type') || '';
    var parsedData = ct.includes('application/json') ? await response.json() : await response.text();

    return {
      data: parsedData,
      status: response.status,
      statusText: response.statusText,
      headers: function() {
        var h = {};
        response.headers.forEach(function(v, k) { h[k] = v; });
        return h;
      },
      config: config,
    };
  } catch (error) {
    throw {
      data: null,
      status: -1,
      statusText: error instanceof Error ? error.message : 'Unknown error',
      headers: function() { return {}; },
      config: config,
      error: error,
    };
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}

/** Legacy toJson from AngularJS — replaces undefined with null. */
export function legacyToJson(value) {
  return JSON.stringify(value, function(k, v) { return v === undefined ? null : v; });
}
