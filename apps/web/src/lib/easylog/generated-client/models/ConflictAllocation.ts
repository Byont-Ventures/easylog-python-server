/* tslint:disable */
/* eslint-disable */
/**
 * Easylog No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.2.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import { mapValues } from '../runtime';
import type { AdditionalAllocationData } from './AdditionalAllocationData';
import {
  AdditionalAllocationDataFromJSON,
  AdditionalAllocationDataFromJSONTyped,
  AdditionalAllocationDataToJSON,
  AdditionalAllocationDataToJSONTyped
} from './AdditionalAllocationData';
import type { ConflictAllocationConflictsInner } from './ConflictAllocationConflictsInner';
import {
  ConflictAllocationConflictsInnerFromJSON,
  ConflictAllocationConflictsInnerFromJSONTyped,
  ConflictAllocationConflictsInnerToJSON,
  ConflictAllocationConflictsInnerToJSONTyped
} from './ConflictAllocationConflictsInner';

/**
 * @export
 * @interface ConflictAllocation
 */
export interface ConflictAllocation {
  /**
   * @memberof ConflictAllocation
   * @type {number}
   */
  id?: number;
  /**
   * @memberof ConflictAllocation
   * @type {number}
   */
  resourceId?: number;
  /**
   * @memberof ConflictAllocation
   * @type {string}
   */
  label?: string;
  /**
   * @memberof ConflictAllocation
   * @type {string}
   */
  type?: string | null;
  /**
   * @memberof ConflictAllocation
   * @type {string}
   */
  group?: string | null;
  /**
   * @memberof ConflictAllocation
   * @type {string}
   */
  comment?: string | null;
  /**
   * @memberof ConflictAllocation
   * @type {Date}
   */
  start?: Date;
  /**
   * @memberof ConflictAllocation
   * @type {Date}
   */
  end?: Date;
  /**
   * @memberof ConflictAllocation
   * @type {AdditionalAllocationData[]}
   */
  fields?: Array<AdditionalAllocationData> | null;
  /**
   * @memberof ConflictAllocation
   * @type {ConflictAllocationConflictsInner[]}
   */
  conflicts?: Array<ConflictAllocationConflictsInner>;
  /**
   * @memberof ConflictAllocation
   * @type {Date}
   */
  createdAt?: Date;
  /**
   * @memberof ConflictAllocation
   * @type {Date}
   */
  updatedAt?: Date;
}

/** Check if a given object implements the ConflictAllocation interface. */
export function instanceOfConflictAllocation(
  value: object
): value is ConflictAllocation {
  return true;
}

export function ConflictAllocationFromJSON(json: any): ConflictAllocation {
  return ConflictAllocationFromJSONTyped(json, false);
}

export function ConflictAllocationFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): ConflictAllocation {
  if (json == null) {
    return json;
  }
  return {
    id: json['id'] == null ? undefined : json['id'],
    resourceId: json['resource_id'] == null ? undefined : json['resource_id'],
    label: json['label'] == null ? undefined : json['label'],
    type: json['type'] == null ? undefined : json['type'],
    group: json['group'] == null ? undefined : json['group'],
    comment: json['comment'] == null ? undefined : json['comment'],
    start: json['start'] == null ? undefined : new Date(json['start']),
    end: json['end'] == null ? undefined : new Date(json['end']),
    fields:
      json['fields'] == null
        ? undefined
        : (json['fields'] as Array<any>).map(AdditionalAllocationDataFromJSON),
    conflicts:
      json['conflicts'] == null
        ? undefined
        : (json['conflicts'] as Array<any>).map(
            ConflictAllocationConflictsInnerFromJSON
          ),
    createdAt:
      json['created_at'] == null ? undefined : new Date(json['created_at']),
    updatedAt:
      json['updated_at'] == null ? undefined : new Date(json['updated_at'])
  };
}

export function ConflictAllocationToJSON(json: any): ConflictAllocation {
  return ConflictAllocationToJSONTyped(json, false);
}

export function ConflictAllocationToJSONTyped(
  value?: ConflictAllocation | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    id: value['id'],
    resource_id: value['resourceId'],
    label: value['label'],
    type: value['type'],
    group: value['group'],
    comment: value['comment'],
    start: value['start'] == null ? undefined : value['start'].toISOString(),
    end: value['end'] == null ? undefined : value['end'].toISOString(),
    fields:
      value['fields'] == null
        ? undefined
        : (value['fields'] as Array<any>).map(AdditionalAllocationDataToJSON),
    conflicts:
      value['conflicts'] == null
        ? undefined
        : (value['conflicts'] as Array<any>).map(
            ConflictAllocationConflictsInnerToJSON
          ),
    created_at:
      value['createdAt'] == null ? undefined : value['createdAt'].toISOString(),
    updated_at:
      value['updatedAt'] == null ? undefined : value['updatedAt'].toISOString()
  };
}
