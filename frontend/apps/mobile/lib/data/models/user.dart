// File: E:/civic-issue-reporter/apps/mobile/lib/data/models/user.dart

class User {
  final String name;
  final String? handle;
  final String? avatarUrl;

  User({
    required this.name,
    this.handle,
    this.avatarUrl,
  });

  // A factory constructor to safely create a User from a JSON map
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      name: json['name'] ?? 'Anonymous',
      handle: json['handle'],
      avatarUrl: json['avatar_url'],
    );
  }
}