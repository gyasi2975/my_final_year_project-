/// A saved analysis entry for history (body part, fracture result, image path, date).
class HistoryEntry {
  final String id;
  final String imagePath;
  final String bodyPartName;
  final bool hasFracture;
  final String fractureTypeName;
  final double fractureConfidence;
  final DateTime date;
  final String? unsuitableReason;

  const HistoryEntry({
    required this.id,
    required this.imagePath,
    required this.bodyPartName,
    required this.hasFracture,
    required this.fractureTypeName,
    required this.fractureConfidence,
    required this.date,
    this.unsuitableReason,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'imagePath': imagePath,
        'bodyPartName': bodyPartName,
        'hasFracture': hasFracture,
        'fractureTypeName': fractureTypeName,
        'fractureConfidence': fractureConfidence,
        'date': date.toIso8601String(),
        if (unsuitableReason != null) 'unsuitableReason': unsuitableReason,
      };

  static HistoryEntry fromJson(Map<String, dynamic> json) => HistoryEntry(
        id: json['id'] as String,
        imagePath: json['imagePath'] as String,
        bodyPartName: json['bodyPartName'] as String,
        hasFracture: json['hasFracture'] as bool,
        fractureTypeName: json['fractureTypeName'] as String,
        fractureConfidence: (json['fractureConfidence'] as num).toDouble(),
        date: DateTime.parse(json['date'] as String),
        unsuitableReason: json['unsuitableReason'] as String?,
      );
}
